from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date, timedelta
from django.utils import timezone

class Brand(models.Model):
    """Brand model"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Brand Name")
    description = models.TextField(blank=True, verbose_name="Brand Description")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Brand"
        verbose_name_plural = "Brands"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Category(models.Model):
    """Cosmetic category"""
    CATEGORY_TYPES = [
        ('skincare', 'Skincare'),
        ('makeup', 'Makeup'),
        ('fragrance', 'Fragrance'),
        ('hair', 'Hair Care'),
        ('body', 'Body Care'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=50, verbose_name="Category Name")
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES, verbose_name="Category Type")
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['category_type', 'name']
        unique_together = ['name', 'category_type']
    
    def __str__(self):
        return f"{self.get_category_type_display()} - {self.name}"

class CosmeticProduct(models.Model):
    """Cosmetic product model"""
    # Basic information
    name = models.CharField(max_length=200, verbose_name="Product Name")
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name="Brand")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name="Category")
    
    # Product details
    shade = models.CharField(max_length=100, blank=True, verbose_name="Shade/Color")
    capacity = models.CharField(max_length=50, blank=True, verbose_name="Capacity")
    
    # Purchase information
    purchase_date = models.DateField(default=date.today, verbose_name="Purchase Date")
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Price")
    purchase_location = models.CharField(max_length=200, blank=True, verbose_name="Purchase Location")
    
    # Expiry management
    production_date = models.DateField(null=True, blank=True, verbose_name="Production Date")
    expiration_date = models.DateField(verbose_name="Expiration Date")
    
    # Usage status
    OPEN_STATUS = [
        ('unopened', 'Unopened'),
        ('opened', 'Opened'),
        ('finished', 'Finished'),
        ('discarded', 'Discarded'),
    ]
    status = models.CharField(max_length=20, choices=OPEN_STATUS, default='unopened', verbose_name="Status")
    opened_date = models.DateField(null=True, blank=True, verbose_name="Opened Date")
    
    # Period After Opening (months)
    pao_after_opening = models.PositiveIntegerField(
        default=12, 
        verbose_name="Period After Opening (months)",
        help_text="Number of months to use after opening"
    )
    
    # User rating
    rating = models.PositiveIntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Rating"
    )
    
    # Additional information
    description = models.TextField(blank=True, verbose_name="Product Description")
    ingredients = models.TextField(blank=True, verbose_name="Ingredients")
    notes = models.TextField(blank=True, verbose_name="Usage Notes")
    
    # Image
    image = models.ImageField(upload_to='cosmetics/', null=True, blank=True, verbose_name="Product Image")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User")
    
    class Meta:
        verbose_name = "Cosmetic Product"
        verbose_name_plural = "Cosmetic Products"
        ordering = ['-purchase_date', 'brand', 'name']
        indexes = [
            models.Index(fields=['expiration_date', 'status']),
            models.Index(fields=['brand', 'category']),
        ]
    
    def __str__(self):
        return f"{self.brand.name} - {self.name}"
    
    @property
    def is_expired(self):
        """Check if product is expired"""
        if self.expiration_date is None:
            return False  # 如果到期时间为空，认为未过期
        return date.today() > self.expiration_date
    
    @property
    def is_expired(self):
        """检查产品是否过期 - 增强版"""
        if self.expiration_date is None:
            return False
        
        # 如果已开封，使用开封后保质期计算
        if self.status == 'opened' and self.opened_date:
            pao_expiry = self.opened_date + timedelta(days=self.pao_after_opening * 30)
            return date.today() > min(self.expiration_date, pao_expiry)
        
        return date.today() > self.expiration_date
    
    @property
    def effective_expiration_date(self):
        """获取实际有效过期日期"""
        if self.status == 'opened' and self.opened_date:
            pao_expiry = self.opened_date + timedelta(days=self.pao_after_opening * 30)
            return min(self.expiration_date, pao_expiry)
        return self.expiration_date
    
    @property
    def days_until_expiration(self):
        """距离过期的天数 - 增强版"""
        effective_date = self.effective_expiration_date
        if effective_date is None:
            return None
        delta = effective_date - date.today()
        return delta.days
    
    @property
    def expiration_status(self):
        """过期状态 - 增强版"""
        if self.effective_expiration_date is None:
            return "unknown"
        
        days = self.days_until_expiration
        
        if days < 0:
            return "expired"
        elif days <= 7:  # 7天内过期 - 紧急
            return "urgent"
        elif days <= 30:  # 30天内过期 - 警告
            return "soon"
        else:
            return "good"
    
    @property
    def expiration_priority(self):
        """过期优先级（用于排序）"""
        status_priority = {
            "expired": 1,
            "urgent": 2, 
            "soon": 3,
            "good": 4,
            "unknown": 5
        }
        return status_priority.get(self.expiration_status, 5)


class CosmeticProductManager(models.Manager):
    def get_expired_products(self, user=None):
        """获取已过期产品"""
        queryset = self.filter(expiration_date__lt=date.today())
        if user:
            queryset = queryset.filter(user=user)
        return queryset
    
    def get_urgent_products(self, user=None):
        """获取7天内过期的产品"""
        today = date.today()
        queryset = self.filter(
            expiration_date__gte=today,
            expiration_date__lte=today + timedelta(days=7)
        )
        if user:
            queryset = queryset.filter(user=user)
        return queryset
    
    def get_soon_expiring_products(self, user=None):
        """获取30天内过期的产品"""
        today = date.today()
        queryset = self.filter(
            expiration_date__gte=today + timedelta(days=8),  # 8天以上
            expiration_date__lte=today + timedelta(days=30)   # 30天以内
        )
        if user:
            queryset = queryset.filter(user=user)
        return queryset
    
    def get_good_products(self, user=None):
        """获取状态良好的产品"""
        today = date.today()
        queryset = self.filter(expiration_date__gt=today + timedelta(days=30))
        if user:
            queryset = queryset.filter(user=user)
        return queryset

class CosmeticProduct(models.Model):
    """Cosmetic product model"""
    
    # 状态选项定义
    OPEN_STATUS = [
        ('unopened', 'Unopened'),
        ('opened', 'Opened'),
        ('finished', 'Finished'),
        ('discarded', 'Discarded'),
    ]
    
    # Basic information
    name = models.CharField(max_length=200, verbose_name="Product Name")
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name="Brand")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name="Category")
    
    # Product details
    shade = models.CharField(max_length=100, blank=True, verbose_name="Shade/Color")
    capacity = models.CharField(max_length=50, blank=True, verbose_name="Capacity")
    
    # Purchase information
    purchase_date = models.DateField(default=date.today, verbose_name="Purchase Date")
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Price")
    purchase_location = models.CharField(max_length=200, blank=True, verbose_name="Purchase Location")
    
    # Expiry management
    production_date = models.DateField(null=True, blank=True, verbose_name="Production Date")
    expiration_date = models.DateField(verbose_name="Expiration Date")
    
    # Usage status - 这里使用已定义的 OPEN_STATUS
    status = models.CharField(max_length=20, choices=OPEN_STATUS, default='unopened', verbose_name="Status")
    opened_date = models.DateField(null=True, blank=True, verbose_name="Opened Date")
    name = models.CharField(max_length=200)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    expiration_date = models.DateField()
    status = models.CharField(max_length=20, choices=OPEN_STATUS, default='unopened')
    
    class Meta:
        # 确保排序字段存在
        ordering = ['expiration_date', 'status']

class UsageLog(models.Model):
    product = models.ForeignKey(CosmeticProduct, on_delete=models.CASCADE, related_name='usage_logs')
    used_at = models.DateTimeField(auto_now_add=True, verbose_name="Used At")
    notes = models.TextField(blank=True, verbose_name="Usage Notes")
    
    class Meta:
        verbose_name = "Usage Log"
        verbose_name_plural = "Usage Logs"
        ordering = ['-used_at']
    def get_product_display(self):
        """用于下拉框显示的产品名称"""
        return f"{self.product.brand.name} - {self.product.name}" if self.product.brand else self.product.name
    
    def __str__(self):
        # 修改这里：显示产品名称而不是对象表示
        return f"{self.product.name} - {self.used_at.strftime('%Y-%m-%d %H:%M')}"