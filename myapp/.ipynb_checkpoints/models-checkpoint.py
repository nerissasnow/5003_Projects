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

class CosmeticProductManager(models.Manager):
    def get_expired_products(self, user=None):
        """Get expired products"""
        queryset = self.filter(expiration_date__lt=date.today())
        if user:
            queryset = queryset.filter(user=user)
        return queryset
    
    def get_urgent_products(self, user=None):
        """Get products expiring within 7 days"""
        today = date.today()
        queryset = self.filter(
            expiration_date__gte=today,
            expiration_date__lte=today + timedelta(days=7)
        )
        if user:
            queryset = queryset.filter(user=user)
        return queryset
    
    def get_soon_expiring_products(self, user=None):
        """Get products expiring within 30 days"""
        today = date.today()
        queryset = self.filter(
            expiration_date__gte=today + timedelta(days=8),  # More than 7 days
            expiration_date__lte=today + timedelta(days=30)   # Within 30 days
        )
        if user:
            queryset = queryset.filter(user=user)
        return queryset
    
    def get_good_products(self, user=None):
        """Get products in good condition"""
        today = date.today()
        queryset = self.filter(expiration_date__gt=today + timedelta(days=30))
        if user:
            queryset = queryset.filter(user=user)
        return queryset

class CosmeticProduct(models.Model):
    """Cosmetic product model"""
    
    # Status options
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
    
    # Usage status
    status = models.CharField(max_length=20, choices=OPEN_STATUS, default='unopened', verbose_name="Status")
    opened_date = models.DateField(null=True, blank=True, verbose_name="Opened Date")
    
    # Period After Opening (months)
    pao_after_opening = models.PositiveIntegerField(
        default=12, 
        verbose_name="Period After Opening (months)",
        help_text="Number of months to use after opening",
        blank=True,   # 允许为空
        null=True     # 数据库允许为空
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
    
    # Custom manager
    objects = CosmeticProductManager()
    
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
        """Check if product is expired - enhanced version"""
        if self.expiration_date is None:
            return False
        
        # If opened, calculate using period after opening
        if self.status == 'opened' and self.opened_date:
            pao_expiry = self.opened_date + timedelta(days=self.pao_after_opening * 30)
            return date.today() > min(self.expiration_date, pao_expiry)
        
        return date.today() > self.expiration_date
    
    @property
    def effective_expiration_date(self):
        """Get actual effective expiration date"""
        if self.status == 'opened' and self.opened_date:
            pao_expiry = self.opened_date + timedelta(days=self.pao_after_opening * 30)
            return min(self.expiration_date, pao_expiry)
        return self.expiration_date
    
    @property
    def days_until_expiration(self):
        """Days until expiration - enhanced version"""
        effective_date = self.effective_expiration_date
        if effective_date is None:
            return None
        delta = effective_date - date.today()
        return delta.days
    
    @property
    def expiration_status(self):
        """Expiration status - enhanced version"""
        if self.effective_expiration_date is None:
            return "unknown"
        
        days = self.days_until_expiration
        
        if days < 0:
            return "expired"
        elif days <= 7:  # Expiring within 7 days - urgent
            return "urgent"
        elif days <= 30:  # Expiring within 30 days - warning
            return "soon"
        else:
            return "good"
    
    @property
    def expiration_priority(self):
        """Expiration priority (for sorting)"""
        status_priority = {
            "expired": 1,
            "urgent": 2, 
            "soon": 3,
            "good": 4,
            "unknown": 5
        }
        return status_priority.get(self.expiration_status, 5)

class UsageLog(models.Model):
    """Usage log model"""
    product = models.ForeignKey(CosmeticProduct, on_delete=models.CASCADE, related_name='usage_logs')
    used_at = models.DateTimeField(auto_now_add=True, verbose_name="Used At")
    notes = models.TextField(blank=True, verbose_name="Usage Notes")
    
    class Meta:
        verbose_name = "Usage Log"
        verbose_name_plural = "Usage Logs"
        ordering = ['-used_at']
    
    def get_product_display(self):
        """Display product name for dropdowns"""
        return f"{self.product.brand.name} - {self.product.name}" if self.product.brand else self.product.name
    
    def __str__(self):
        # Modified: show product name instead of object representation
        return f"{self.product.name} - {self.used_at.strftime('%Y-%m-%d %H:%M')}"