from datetime import date, timedelta
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, When, Value, IntegerField, Q
from django.contrib import messages
from django.http import Http404
from .models import CosmeticProduct, Brand, Category

# 核心修改：重写 ListView 的分页逻辑，彻底避免 self.kwargs 依赖
class CustomPaginatorListView(LoginRequiredMixin, ListView):
    """自定义分页基类，解决原 ListView 分页 kwargs 错误"""
    paginate_by = 10

    def paginate_queryset(self, queryset, page_size):  # 修复方法名
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
        """获取筛选后的产品列表"""
        queryset = CosmeticProduct.objects.filter(user=self.request.user)
        
        # 获取筛选参数
        status_filter = self.request.GET.get('status', '')
        category_filter = self.request.GET.get('category', '')
        search_query = self.request.GET.get('search', '')
        
        # 应用状态筛选
        if status_filter:
            today = date.today()
            if status_filter == 'expired':
                queryset = queryset.filter(expiration_date__lt=today)
            elif status_filter == 'urgent':
                queryset = queryset.filter(
                    expiration_date__gte=today,
                    expiration_date__lte=today + timedelta(days=7)
                )
            elif status_filter == 'soon':
                queryset = queryset.filter(
                    expiration_date__gt=today + timedelta(days=7),
                    expiration_date__lte=today + timedelta(days=30)
                )
            elif status_filter == 'good':
                queryset = queryset.filter(expiration_date__gt=today + timedelta(days=30))
        
        # 应用分类筛选
        if category_filter:
            queryset = queryset.filter(category_id=category_filter)
        
        # 应用搜索筛选
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(brand__name__icontains=search_query) |
                Q(category__name__icontains=search_query) |
                Q(shade__icontains=search_query)
            )
        
        return queryset.order_by('expiration_date')

    def get_context_data(self, **kwargs):
        """添加上下文数据"""
        context = super().get_context_data(**kwargs)
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
        
        # 添加所有品牌和分类用于下拉框
        context['brands'] = Brand.objects.all()  # 添加品牌数据
        context['categories'] = Category.objects.all()
        
        # 添加当前筛选参数
        context['current_status'] = self.request.GET.get('status', '')
        context['current_category'] = self.request.GET.get('category', '')
        context['current_search'] = self.request.GET.get('search', '')
        
        return context

class CosmeticProductDetailView(LoginRequiredMixin, DetailView):
    model = CosmeticProduct
    template_name = 'myapp/product_detail.html'
    context_object_name = 'product'
    
    def get_queryset(self):
        """确保用户只能访问自己的产品"""
        return CosmeticProduct.objects.filter(user=self.request.user)
    
    def get_object(self, queryset=None):
        """重写get_object方法添加错误处理"""
        try:
            # 调用父类方法获取对象
            obj = super().get_object(queryset)
            # 验证对象存在且属于当前用户
            if obj.user != self.request.user:
                raise Http404("您没有权限查看此产品")
            return obj
        except (CosmeticProduct.DoesNotExist, ValueError):
            raise Http404("产品不存在")
    
    def get_context_data(self, **kwargs):
        """添加上下文数据，包括天数计算和状态"""
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        today = date.today()
        
        # 计算距离过期的天数
        if product.expiration_date:
            days_until_expiration = (product.expiration_date - today).days
            context['days_until_expiration'] = days_until_expiration
            
            # 根据天数设置状态和样式
            if days_until_expiration < 0:
                context['expiration_status'] = 'expired'
                context['status_class'] = 'danger'  # Bootstrap danger class for red
                context['status_icon'] = 'fa-times-circle'
                context['status_text'] = f'Expired {abs(days_until_expiration)} days ago'
            elif days_until_expiration <= 7:
                context['expiration_status'] = 'urgent'
                context['status_class'] = 'warning'  # Bootstrap warning class for yellow
                context['status_icon'] = 'fa-exclamation-triangle'
                context['status_text'] = f'{days_until_expiration} days until expiration - URGENT'
            elif days_until_expiration <= 30:
                context['expiration_status'] = 'soon'
                context['status_class'] = 'info'     # Bootstrap info class for blue
                context['status_icon'] = 'fa-clock'
                context['status_text'] = f'{days_until_expiration} days until expiration - SOON'
            else:
                context['expiration_status'] = 'good'
                context['status_class'] = 'success'  # Bootstrap success class for green
                context['status_icon'] = 'fa-check-circle'
                context['status_text'] = f'{days_until_expiration} days until expiration - GOOD'
        else:
            context['days_until_expiration'] = None
            context['expiration_status'] = 'unknown'
            context['status_class'] = 'secondary'   # Bootstrap secondary class for gray
            context['status_icon'] = 'fa-question-circle'
            context['status_text'] = 'Expiration date not set'
        
        return context

class CosmeticProductCreateView(LoginRequiredMixin, CreateView):
    model = CosmeticProduct
    template_name = 'myapp/product_form.html'
    fields = ['name', 'brand', 'category', 'shade', 'capacity', 
              'purchase_date', 'price', 'purchase_location',
              'expiration_date', 'status', 'opened_date', 'pao_after_opening',
              'rating', 'description', 'ingredients', 'notes', 'image']
    
    def get_success_url(self):
        return reverse_lazy('myapp:product_list')
    
    def get_initial(self):
        """设置表单字段的初始值"""
        initial = super().get_initial()
        # 为pao_after_opening设置默认值
        initial['pao_after_opening'] = 12  # 默认12个月
        return initial
    
    def get_context_data(self, **kwargs):
        """关键修复：添加上下文数据，包括品牌和分类"""
        context = super().get_context_data(**kwargs)
        # 添加所有品牌和分类用于下拉框
        context['brands'] = Brand.objects.all()
        context['categories'] = Category.objects.all()
        return context
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        # 如果pao_after_opening为空，设置默认值
        if not form.cleaned_data.get('pao_after_opening'):
            form.instance.pao_after_opening = 12
        messages.success(self.request, '产品添加成功！')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """表单验证失败时调用"""
        # 添加详细的错误信息
        if 'pao_after_opening' in form.errors:
            messages.error(self.request, '请填写"开封后使用期限"字段或接受默认值')
        return super().form_invalid(form)

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
    
    def get_initial(self):
        """设置表单字段的初始值"""
        initial = super().get_initial()
        # 如果pao_after_opening为空，设置默认值
        if not initial.get('pao_after_opening'):
            initial['pao_after_opening'] = 12
        return initial
    
    def get_context_data(self, **kwargs):
        """关键修复：添加上下文数据，包括品牌和分类"""
        context = super().get_context_data(**kwargs)
        # 添加所有品牌和分类用于下拉框
        context['brands'] = Brand.objects.all()
        context['categories'] = Category.objects.all()
        return context
    
    def form_valid(self, form):
        # 如果pao_after_opening为空，设置默认值
        if not form.cleaned_data.get('pao_after_opening'):
            form.instance.pao_after_opening = 12
        messages.success(self.request, '产品更新成功！')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """表单验证失败时调用"""
        # 添加详细的错误信息
        if 'pao_after_opening' in form.errors:
            messages.error(self.request, '请填写"开封后使用期限"字段或接受默认值')
        messages.error(self.request, '请检查表单中的错误并重新提交。')
        return super().form_invalid(form)

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
        context = super().get_context_data(**kwargs)
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