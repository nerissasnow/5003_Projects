from datetime import date, timedelta
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, When, Value, IntegerField, Q
from django.contrib import messages
from django.http import Http404
from .models import CosmeticProduct, Brand, Category
from django.contrib.auth.views import LoginView, LogoutView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _


# Core modification: Rewrite ListView pagination logic to completely avoid self.kwargs dependency
class CustomPaginatorListView(LoginRequiredMixin, ListView):
    """Custom pagination base class to solve original ListView pagination kwargs error"""
    paginate_by = 10

    def paginate_queryset(self, queryset, page_size):
        from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
        # Manually initialize paginator, get page number from request.GET (not relying on self.kwargs)
        paginator = Paginator(queryset, page_size)
        page = self.request.GET.get('page', 1)  # Default to page 1
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            # When page is not an integer, return first page
            page_obj = paginator.page(1)
        except EmptyPage:
            # When page is out of range, return last page
            page_obj = paginator.page(paginator.num_pages)
        # Return 4 required parameters for pagination (following ListView specification)
        return (paginator, page_obj, page_obj.object_list, page_obj.has_other_pages())

# Inherit custom pagination base class, replace original ListView
class CosmeticProductListView(CustomPaginatorListView):
    model = CosmeticProduct
    template_name = 'myapp/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        """Get filtered product list"""
        queryset = CosmeticProduct.objects.filter(user=self.request.user)
        
        # Get filter parameters
        status_filter = self.request.GET.get('status', '')
        category_filter = self.request.GET.get('category', '')
        search_query = self.request.GET.get('search', '')
        
        # Apply status filter
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
        
        # Apply category filter
        if category_filter:
            queryset = queryset.filter(category_id=category_filter)
        
        # Apply search filter
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(brand__name__icontains=search_query) |
                Q(category__name__icontains=search_query) |
                Q(shade__icontains=search_query)
            )
        
        return queryset.order_by('expiration_date')

    def get_context_data(self, **kwargs):
        """Add context data"""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Add product count statistics for various statuses
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
        
        # Add all brands and categories for dropdowns
        context['brands'] = Brand.objects.all()
        context['categories'] = Category.objects.all()
        
        # Add current filter parameters
        context['current_status'] = self.request.GET.get('status', '')
        context['current_category'] = self.request.GET.get('category', '')
        context['current_search'] = self.request.GET.get('search', '')
        
        return context

class CosmeticProductDetailView(LoginRequiredMixin, DetailView):
    model = CosmeticProduct
    template_name = 'myapp/product_detail.html'
    context_object_name = 'product'
    
    def get_queryset(self):
        """Ensure users can only access their own products"""
        return CosmeticProduct.objects.filter(user=self.request.user)
    
    def get_object(self, queryset=None):
        """Override get_object method to add error handling"""
        try:
            # Call parent method to get object
            obj = super().get_object(queryset)
            # Verify object exists and belongs to current user
            if obj.user != self.request.user:
                raise Http404("You do not have permission to view this product")
            return obj
        except (CosmeticProduct.DoesNotExist, ValueError):
            raise Http404("Product does not exist")
    
    def get_context_data(self, **kwargs):
        """Add context data including day calculation and status"""
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        today = date.today()
        
        # Calculate days until expiration
        if product.expiration_date:
            days_until_expiration = (product.expiration_date - today).days
            context['days_until_expiration'] = days_until_expiration
            
            # Set status and style based on days
            if days_until_expiration < 0:
                context['expiration_status'] = 'expired'
                context['status_class'] = 'danger'
                context['status_icon'] = 'fa-times-circle'
                context['status_text'] = f'Expired {abs(days_until_expiration)} days ago'
            elif days_until_expiration <= 7:
                context['expiration_status'] = 'urgent'
                context['status_class'] = 'warning'
                context['status_icon'] = 'fa-exclamation-triangle'
                context['status_text'] = f'{days_until_expiration} days until expiration - URGENT'
            elif days_until_expiration <= 30:
                context['expiration_status'] = 'soon'
                context['status_class'] = 'info'
                context['status_icon'] = 'fa-clock'
                context['status_text'] = f'{days_until_expiration} days until expiration - SOON'
            else:
                context['expiration_status'] = 'good'
                context['status_class'] = 'success'
                context['status_icon'] = 'fa-check-circle'
                context['status_text'] = f'{days_until_expiration} days until expiration - GOOD'
        else:
            context['days_until_expiration'] = None
            context['expiration_status'] = 'unknown'
            context['status_class'] = 'secondary'
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
        """Set initial values for form fields"""
        initial = super().get_initial()
        # Set default value for pao_after_opening
        initial['pao_after_opening'] = 12  # Default 12 months
        return initial
    
    def get_context_data(self, **kwargs):
        """Key fix: Add context data including brands and categories"""
        context = super().get_context_data(**kwargs)
        # Add all brands and categories for dropdowns
        context['brands'] = Brand.objects.all()
        context['categories'] = Category.objects.all()
        return context
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        # If pao_after_opening is empty, set default value
        if not form.cleaned_data.get('pao_after_opening'):
            form.instance.pao_after_opening = 12
        messages.success(self.request, 'Product added successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Called when form validation fails"""
        # Add detailed error message
        if 'pao_after_opening' in form.errors:
            messages.error(self.request, 'Please fill in the "Period After Opening" field or accept the default value')
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
        """Set initial values for form fields"""
        initial = super().get_initial()
        # If pao_after_opening is empty, set default value
        if not initial.get('pao_after_opening'):
            initial['pao_after_opening'] = 12
        return initial
    
    def get_context_data(self, **kwargs):
        """Key fix: Add context data including brands and categories"""
        context = super().get_context_data(**kwargs)
        # Add all brands and categories for dropdowns
        context['brands'] = Brand.objects.all()
        context['categories'] = Category.objects.all()
        return context
    
    def form_valid(self, form):
        # If pao_after_opening is empty, set default value
        if not form.cleaned_data.get('pao_after_opening'):
            form.instance.pao_after_opening = 12
        messages.success(self.request, 'Product updated successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Called when form validation fails"""
        # Add detailed error message
        if 'pao_after_opening' in form.errors:
            messages.error(self.request, 'Please fill in the "Period After Opening" field or accept the default value')
        messages.error(self.request, 'Please check the form for errors and resubmit.')
        return super().form_invalid(form)

class CosmeticProductDeleteView(LoginRequiredMixin, DeleteView):
    model = CosmeticProduct
    template_name = 'myapp/product_confirm_delete.html'
    success_url = reverse_lazy('myapp:product_list')
    
    def get_queryset(self):
        return CosmeticProduct.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Product deleted successfully!')
        return super().delete(request, *args, **kwargs)

class ExpiringProductsView(LoginRequiredMixin, TemplateView):
    """Dedicated page for displaying expiring products"""
    template_name = 'myapp/expiring_products.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = date.today()
        
        # Get products in various statuses
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


# 修复登录视图
class CustomLoginView(LoginView):
    """自定义登录视图，修复登录消息问题"""
    template_name = 'myapp/login.html'
    
    def get_success_url(self):
        # 确保重定向到产品列表
        return reverse_lazy('myapp:product_list')
    
    def form_valid(self, form):
        # 清除所有现有消息
        storage = messages.get_messages(self.request)
        for message in storage:
            pass  # 标记所有消息为已读
        
        response = super().form_valid(form)
        
        # 仅在成功登录后添加欢迎消息
        messages.success(self.request, _('Login successful! Welcome back, %(username)s.') % {
            'username': self.request.user.username
        })
        return response
    
    def form_invalid(self, form):
        # 清除现有消息
        storage = messages.get_messages(self.request)
        for message in storage:
            pass
        
        # 添加登录失败消息
        messages.error(self.request, _('Please enter a correct username and password.'))
        return super().form_invalid(form)

class CustomLogoutView(LogoutView):
    """自定义退出视图 - 移除退出消息"""
    next_page = 'myapp:login'
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        # 清除所有消息，但不添加新消息
        storage = messages.get_messages(request)
        for message in storage:
            pass
        
        # 直接调用父类方法，不添加退出消息
        return super().dispatch(request, *args, **kwargs)