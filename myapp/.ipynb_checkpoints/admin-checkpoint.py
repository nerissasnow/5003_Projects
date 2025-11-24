from django.contrib import admin
from .models import Brand, Category, CosmeticProduct, UsageLog

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type']
    list_filter = ['category_type']
    search_fields = ['name']

class UsageLogInline(admin.TabularInline):
    model = UsageLog
    extra = 0

@admin.register(CosmeticProduct)
class CosmeticProductAdmin(admin.ModelAdmin):
    # 确保字段名正确
    list_display = ['name', 'brand', 'category', 'expiration_date', 'status']
    
    # 确保过滤器字段正确
    list_filter = ['status', 'expiration_date', 'brand', 'category']
    
    # 添加搜索字段
    search_fields = ['name', 'brand__name']
    
    def expiration_status_column(self, obj):
        """在admin中显示带颜色的过期状态"""
        status = obj.expiration_status
        colors = {
            'good': 'green',
            'soon': 'orange', 
            'urgent': 'red',
            'expired': 'darkred',
            'unknown': 'gray'
        }
        from django.utils.html import format_html
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(status, 'black'),
            status.upper()
        )
    expiration_status_column.short_description = 'Expiration Status'
    
    def days_until_column(self, obj):
        """显示距离过期的天数"""
        days = obj.days_until_expiration
        if days is None:
            return "Unknown"
        elif days < 0:
            return f"Expired ({abs(days)} days ago)"
        else:
            return f"{days} days"
    days_until_column.short_description = 'Days Until Expiration'
    
    def is_expired_column(self, obj):
        """显示是否过期的图标"""
        if obj.is_expired:
            return '❌ EXPIRED'
        else:
            return '✅ OK'
    is_expired_column.short_description = 'Is Expired'
    
    # 添加按过期状态过滤
    class ExpirationStatusFilter(admin.SimpleListFilter):
        title = 'Expiration Status'
        parameter_name = 'exp_status'
        
        def lookups(self, request, model_admin):
            return [
                ('expired', 'Expired'),
                ('urgent', 'Urgent (≤7 days)'),
                ('soon', 'Soon (8-30 days)'),
                ('good', 'Good (>30 days)'),
                ('unknown', 'Unknown'),
            ]
        
        def queryset(self, request, queryset):
            from datetime import date, timedelta
            today = date.today()
            
            if self.value() == 'expired':
                return queryset.filter(expiration_date__lt=today)
            elif self.value() == 'urgent':
                return queryset.filter(
                    expiration_date__gte=today,
                    expiration_date__lte=today + timedelta(days=7)
                )
            elif self.value() == 'soon':
                return queryset.filter(
                    expiration_date__gte=today + timedelta(days=8),
                    expiration_date__lte=today + timedelta(days=30)
                )
            elif self.value() == 'good':
                return queryset.filter(expiration_date__gt=today + timedelta(days=30))
            elif self.value() == 'unknown':
                return queryset.filter(expiration_date__isnull=True)
    
    list_filter = [ExpirationStatusFilter] + list_filter
    
    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = 'Is Expired'

@admin.register(UsageLog)
class UsageLogAdmin(admin.ModelAdmin):
    list_display = ['get_product_name', 'formatted_used_at', 'notes']
    list_filter = ['used_at', 'product']
    search_fields = ['product__name', 'notes']
    
    def get_product_name(self, obj):
        """显示产品名称"""
        return obj.product.name
    get_product_name.short_description = 'Product Name'
    get_product_name.admin_order_field = 'product__name'
    
    def formatted_used_at(self, obj):
        """格式化使用时间显示"""
        return obj.used_at.strftime('%Y-%m-%d %H:%M')
    formatted_used_at.short_description = 'Used At'
    formatted_used_at.admin_order_field = 'used_at'
