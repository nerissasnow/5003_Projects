from datetime import date, timedelta
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.db.models import Case, When, Value, IntegerField, ExpressionWrapper, F, DurationField
from django.db.models.functions import Cast
from django.db import models
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import CosmeticProduct
from django.urls import reverse_lazy

class CosmeticProductListView(LoginRequiredMixin, ListView):
    model = CosmeticProduct
    template_name = 'cosmetics/product_list.html'
    context_object_name = 'products'
    paginate_by = 20  # 添加分页，每页20个产品
    
    def get_queryset(self):
        """获取查询集，添加过期状态注解"""
        queryset = CosmeticProduct.objects.filter(user=self.request.user)
        
        # 使用数据库函数计算天数
        queryset = queryset.annotate(
            days_until=ExpressionWrapper(
                F('expiration_date') - date.today(),
                output_field=DurationField()
            )
        ).annotate(
            days_int=Cast('days_until', IntegerField())
        )
        
        # 添加过期状态注解
        queryset = queryset.annotate(
            exp_status=Case(
                When(expiration_date__isnull=True, then=Value('unknown')),
                When(days_int__lt=0, then=Value('expired')),
                When(days_int__lte=7, then=Value('urgent')),
                When(days_int__lte=30, then=Value('soon')),
                default=Value('good'),
                output_field=models.CharField()
            )
        )
        
        # 按过期状态和日期排序（过期和即将过期的优先）
        return queryset.order_by('expiration_date')
    
    def get_context_data(self, **kwargs):
        """添加上下文数据"""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # 添加各种状态的产品数量统计
        today = date.today()
        
        # 使用更高效的方法计算数量
        all_products = CosmeticProduct.objects.filter(user=user)
        expired_count = all_products.filter(expiration_date__lt=today).count()
        urgent_count = all_products.filter(
            expiration_date__gte=today,
            expiration_date__lte=today + timedelta(days=7)
        ).count()
        soon_count = all_products.filter(
            expiration_date__gt=today + timedelta(days=7),
            expiration_date__lte=today + timedelta(days=30)
        ).count()
        good_count = all_products.filter(expiration_date__gt=today + timedelta(days=30)).count()
        
        context.update({
            'expired_count': expired_count,
            'urgent_count': urgent_count,
            'soon_count': soon_count,
            'good_count': good_count,
            'total_count': all_products.count(),
            'today': today,
        })
        
        return context

class ExpiringProductsView(LoginRequiredMixin, TemplateView):
    """显示即将过期产品的专用页面"""
    template_name = 'cosmetics/expiring_products.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # 获取各种状态的产品
        today = date.today()
        
        # 使用直接查询而不是管理器方法，避免可能的循环导入问题
        expired_products = CosmeticProduct.objects.filter(
            user=user,
            expiration_date__lt=today
        ).order_by('expiration_date')
        
        urgent_products = CosmeticProduct.objects.filter(
            user=user,
            expiration_date__gte=today,
            expiration_date__lte=today + timedelta(days=7)
        ).order_by('expiration_date')
        
        soon_products = CosmeticProduct.objects.filter(
            user=user,
            expiration_date__gt=today + timedelta(days=7),
            expiration_date__lte=today + timedelta(days=30)
        ).order_by('expiration_date')
        
        context.update({
            'expired_products': expired_products,
            'urgent_products': urgent_products,
            'soon_products': soon_products,
            'today': today,
        })
        
        return context

# 添加其他必要的视图
class CosmeticProductDetailView(LoginRequiredMixin, DetailView):
    model = CosmeticProduct
    template_name = 'cosmetics/product_detail.html'
    
    def get_queryset(self):
        return CosmeticProduct.objects.filter(user=self.request.user)

class CosmeticProductCreateView(LoginRequiredMixin, CreateView):
    model = CosmeticProduct
    template_name = 'cosmetics/product_form.html'
    fields = ['name', 'brand', 'category', 'shade', 'capacity', 
              'purchase_date', 'price', 'purchase_location',
              'expiration_date', 'status', 'opened_date', 'pao_after_opening',
              'rating', 'description', 'ingredients', 'notes', 'image']
    
    def get_success_url(self):
        from django.urls import reverse_lazy
        return reverse_lazy('cosmetics:product_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class CosmeticProductUpdateView(LoginRequiredMixin, UpdateView):
    model = CosmeticProduct
    template_name = 'cosmetics/product_form.html'
    fields = ['name', 'brand', 'category', 'shade', 'capacity', 
              'purchase_date', 'price', 'purchase_location',
              'expiration_date', 'status', 'opened_date', 'pao_after_opening',
              'rating', 'description', 'ingredients', 'notes', 'image']
    
    def get_success_url(self):
        from django.urls import reverse_lazy
        return reverse_lazy('cosmetics:product_list')
    
    def get_queryset(self):
        return CosmeticProduct.objects.filter(user=self.request.user)

class CosmeticProductDeleteView(LoginRequiredMixin, DeleteView):
    model = CosmeticProduct
    template_name = 'cosmetics/product_confirm_delete.html'
    success_url = reverse_lazy('cosmetics:product_list')
    
    def get_queryset(self):
        return CosmeticProduct.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, '产品删除成功！')
        return response