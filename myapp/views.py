from datetime import date, timedelta
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, When, Value, IntegerField
from django.contrib import messages
from .models import CosmeticProduct, Brand, Category

# 核心修改：重写 ListView 的分页逻辑，彻底避免 self.kwargs 依赖
class CustomPaginatorListView(LoginRequiredMixin, ListView):
    """自定义分页基类，解决原 ListView 分页 kwargs 错误"""
    paginate_by = 10

    def paginate_queryset(self, queryset, page_size):
        from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
        # 手动初始化分页器，从 request.GET 获取页码（不依赖 self.kwargs）
        paginator = Paginator(queryset, page_size)
        page = self.request.GET.get('page', 1)  # 默认为第 1 页
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            # 页码不是整数时，返回第 1 页
            page_obj = paginator.page(1)
        except EmptyPage:
            # 页码超出范围时，返回最后一页
            page_obj = paginator.page(paginator.num_pages)
        # 返回分页必需的 4 个参数（遵循 ListView 规范）
        return (paginator, page_obj, page_obj.object_list, page_obj.has_other_pages())

# 继承自定义分页基类，替代原来的 ListView
class CosmeticProductListView(CustomPaginatorListView):
    model = CosmeticProduct
    template_name = 'myapp/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        return CosmeticProduct.objects.filter(user=self.request.user).order_by('expiration_date')

    def get_context_data(self, **kwargs):
        """添加上下文数据"""
        context = super().get_context_data(** kwargs)
        user = self.request.user
        
        # 添加各种状态的产品数量统计
        today = date.today()
        all_products = CosmeticProduct.objects.filter(user=user)
        
        context['expired_count'] = all_products.filter(expiration_date__lt=today).count()
        context['urgent_count'] = all_products.filter(
            expiration_date__gte=today,
            expiration_date__lte=today + timedelta(days=7)
        ).count()
        context['soon_count'] = all_products.filter(
            expiration_date__gt=today + timedelta(days=7),
            expiration_date__lte=today + timedelta(days=30)
        ).count()
        context['good_count'] = all_products.filter(expiration_date__gt=today + timedelta(days=30)).count()
        context['total_count'] = all_products.count()
        context['today'] = today
        
        return context

# 以下视图类无需修改，保持原样
class CosmeticProductDetailView(LoginRequiredMixin, DetailView):
    model = CosmeticProduct
    template_name = 'myapp/product_detail.html'
    
    def get_queryset(self):
        return CosmeticProduct.objects.filter(user=self.request.user)

class CosmeticProductCreateView(LoginRequiredMixin, CreateView):
    model = CosmeticProduct
    template_name = 'myapp/product_form.html'
    fields = ['name', 'brand', 'category', 'shade', 'capacity', 
              'purchase_date', 'price', 'purchase_location',
              'expiration_date', 'status', 'opened_date', 'pao_after_opening',
              'rating', 'description', 'ingredients', 'notes', 'image']
    
    def get_success_url(self):
        return reverse_lazy('myapp:product_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, '产品添加成功！')
        return super().form_valid(form)

class CosmeticProductUpdateView(LoginRequiredMixin, UpdateView):
    model = CosmeticProduct
    template_name = 'myapp/product_form.html'
    fields = ['name', 'brand', 'category', 'shade', 'capacity', 
              'purchase_date', 'price', 'purchase_location',
              'expiration_date', 'status', 'opened_date', 'pao_after_opening',
              'rating', 'description', 'ingredients', 'notes', 'image']
    
    def get_success_url(self):
        return reverse_lazy('myapp:product_list')
    
    def get_queryset(self):
        return CosmeticProduct.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, '产品更新成功！')
        return super().form_valid(form)

class CosmeticProductDeleteView(LoginRequiredMixin, DeleteView):
    model = CosmeticProduct
    template_name = 'myapp/product_confirm_delete.html'
    success_url = reverse_lazy('myapp:product_list')
    
    def get_queryset(self):
        return CosmeticProduct.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, '产品删除成功！')
        return super().delete(request, *args, **kwargs)

class ExpiringProductsView(LoginRequiredMixin, TemplateView):
    """显示即将过期产品的专用页面"""
    template_name = 'myapp/expiring_products.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(** kwargs)
        user = self.request.user
        today = date.today()
        
        # 获取各种状态的产品
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