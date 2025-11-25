import os
import django
from datetime import date, timedelta
import random

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from myapp.models import Brand, Category, CosmeticProduct, UsageLog

def create_sample_data():
    """Create sample data in English"""
    
    # 1. Create or get user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"Created user: {user.username}")
    else:
        print(f"Using existing user: {user.username}")
    
    # 2. Create brands
    brands_data = [
        {"name": "L'Oréal", "description": "French leading cosmetics company"},
        {"name": "Maybelline", "description": "American mass-market cosmetics brand"},
        {"name": "Estée Lauder", "description": "High-end skincare and cosmetics"},
        {"name": "MAC", "description": "Professional makeup brand"},
        {"name": "NARS", "description": "Fashion-forward makeup brand"},
        {"name": "The Ordinary", "description": "Skincare with transparent ingredients"},
        {"name": "La Roche-Posay", "description": "Dermatological skincare brand"},
        {"name": "CeraVe", "description": "Dermatologist-recommended skincare"},
        {"name": "Fenty Beauty", "description": "Inclusive beauty brand by Rihanna"},
        {"name": "Glossier", "description": "Minimalist natural beauty brand"},
    ]
    
    brands = []
    for brand_data in brands_data:
        brand, created = Brand.objects.get_or_create(
            name=brand_data["name"],
            defaults={"description": brand_data["description"]}
        )
        brands.append(brand)
        if created:
            print(f"Created brand: {brand.name}")
    
    # 3. Create categories
    categories_data = [
        # Skincare categories
        {"name": "Cleanser", "category_type": "skincare"},
        {"name": "Serum", "category_type": "skincare"},
        {"name": "Moisturizer", "category_type": "skincare"},
        {"name": "Sunscreen", "category_type": "skincare"},
        {"name": "Toner", "category_type": "skincare"},
        
        # Makeup categories
        {"name": "Foundation", "category_type": "makeup"},
        {"name": "Lipstick", "category_type": "makeup"},
        {"name": "Mascara", "category_type": "makeup"},
        {"name": "Eyeshadow", "category_type": "makeup"},
        {"name": "Blush", "category_type": "makeup"},
        
        # Fragrance categories
        {"name": "Perfume", "category_type": "fragrance"},
        {"name": "Cologne", "category_type": "fragrance"},
        
        # Hair care categories
        {"name": "Shampoo", "category_type": "hair"},
        {"name": "Conditioner", "category_type": "hair"},
        {"name": "Hair Mask", "category_type": "hair"},
        
        # Body care categories
        {"name": "Body Lotion", "category_type": "body"},
        {"name": "Body Wash", "category_type": "body"},
        {"name": "Hand Cream", "category_type": "body"},
    ]
    
    categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data["name"],
            category_type=cat_data["category_type"]
        )
        categories.append(category)
        if created:
            print(f"Created category: {category.name} ({category.get_category_type_display()})")
    
    # 4. Create products with different expiration statuses
    products_data = [
        # Skincare products (good status)
        {
            "name": "Hydrating Moisturizer", "brand": "L'Oréal", "category": "Moisturizer",
            "shade": "N/A", "capacity": "50ml", "price": 25.99,
            "description": "Deep hydration for dry skin"
        },
        {
            "name": "Vitamin C Serum", "brand": "The Ordinary", "category": "Serum", 
            "shade": "N/A", "capacity": "30ml", "price": 12.80,
            "description": "Brightens skin tone, antioxidant properties"
        },
        {
            "name": "SPF 50 Sunscreen", "brand": "La Roche-Posay", "category": "Sunscreen",
            "shade": "N/A", "capacity": "50ml", "price": 35.50,
            "description": "High protection, non-greasy formula"
        },
        
        # Makeup products (soon expiring)
        {
            "name": "Matte Lipstick", "brand": "MAC", "category": "Lipstick",
            "shade": "Ruby Woo", "capacity": "3g", "price": 19.99,
            "description": "Classic matte red finish"
        },
        {
            "name": "Longwear Foundation", "brand": "Estée Lauder", "category": "Foundation",
            "shade": "Ivory", "capacity": "30ml", "price": 42.00,
            "description": "24-hour lasting coverage"
        },
        {
            "name": "Volumizing Mascara", "brand": "Maybelline", "category": "Mascara",
            "shade": "Black", "capacity": "9ml", "price": 9.99,
            "description": "Waterproof and smudge-proof"
        },
        {
            "name": "Eyeshadow Palette", "brand": "NARS", "category": "Eyeshadow",
            "shade": "Suede", "capacity": "5g", "price": 59.00,
            "description": "Smooth texture, easy to blend"
        },
        
        # Products expiring soon (urgent status)
        {
            "name": "Anti-Aging Serum", "brand": "Estée Lauder", "category": "Serum",
            "shade": "N/A", "capacity": "50ml", "price": 85.00,
            "description": "Reduces wrinkles, firms skin"
        },
        {
            "name": "Hydrating Mist", "brand": "CeraVe", "category": "Toner",
            "shade": "N/A", "capacity": "100ml", "price": 15.99,
            "description": "Instant hydration, soothes skin"
        },
        
        # Expired products
        {
            "name": "Brightening Serum", "brand": "L'Oréal", "category": "Serum",
            "shade": "N/A", "capacity": "30ml", "price": 29.99,
            "description": "Even skin tone, fade dark spots"
        },
    ]
    
    # Generate different expiration dates
    today = date.today()
    expiration_dates = [
        today + timedelta(days=365),  # 1 year from now
        today + timedelta(days=180),  # 6 months from now
        today + timedelta(days=90),   # 3 months from now
        today + timedelta(days=45),   # 45 days from now
        today + timedelta(days=15),   # 15 days from now (soon)
        today + timedelta(days=5),    # 5 days from now (urgent)
        today - timedelta(days=30),   # expired 30 days ago
        today - timedelta(days=10),   # expired 10 days ago
        today + timedelta(days=200),  # 200 days from now
        today + timedelta(days=60),   # 60 days from now
    ]
    
    status_options = ['unopened', 'opened', 'finished', 'discarded']
    purchase_locations = ["Sephora", "Ulta", "Official Website", "Department Store", "Drugstore"]
    
    products = []
    for i, product_data in enumerate(products_data):
        # Get brand and category objects
        brand = next((b for b in brands if b.name == product_data["brand"]), brands[0])
        category = next((c for c in categories if c.name == product_data["category"]), categories[0])
        
        # Set different expiration dates and status
        expiration_date = expiration_dates[i % len(expiration_dates)]
        status = status_options[i % len(status_options)]
        opened_date = None
        if status == 'opened':
            opened_date = today - timedelta(days=random.randint(1, 90))
        
        # Create product
        product = CosmeticProduct.objects.create(
            name=product_data["name"],
            brand=brand,
            category=category,
            user=user,
            shade=product_data["shade"],
            capacity=product_data["capacity"],
            purchase_date=today - timedelta(days=random.randint(1, 365)),
            price=product_data["price"],
            purchase_location=random.choice(purchase_locations),
            expiration_date=expiration_date,
            status=status,
            opened_date=opened_date,
            pao_after_opening=random.choice([6, 12, 18, 24]),
            rating=random.choice([None, 4, 5, 3]),
            description=product_data["description"],
            ingredients="Aqua, Glycerin, Vitamin C, Hyaluronic Acid, etc.",
            notes=random.choice(["Love this product", "Would repurchase", "Average results", "Perfect for my skin type"]),
        )
        products.append(product)
        print(f"Created product: {product.name}")
    
    # 5. Create usage logs for some products
    usage_notes = [
        "Great texture, absorbs quickly",
        "Good moisturizing effect",
        "Very natural color",
        "Long lasting wear",
        "A bit drying, need to prep skin well",
        "Nice fragrance",
        "Beautiful packaging",
        "Great value for money",
        "Might cause irritation",
        "Recommended to friends"
    ]
    
    for product in products[:5]:  # Create usage logs for first 5 products
        for _ in range(random.randint(1, 5)):
            UsageLog.objects.create(
                product=product,
                notes=random.choice(usage_notes)
            )
        print(f"Created usage logs for {product.name}")
    
    print("\n" + "="*50)
    print("Sample data creation completed!")
    print(f"Created {len(brands)} brands")
    print(f"Created {len(categories)} categories")
    print(f"Created {len(products)} products")
    print(f"Created {UsageLog.objects.count()} usage logs")
    
    # Show expiration status statistics
    expired = CosmeticProduct.objects.filter(expiration_date__lt=today).count()
    urgent = CosmeticProduct.objects.filter(
        expiration_date__gte=today,
        expiration_date__lte=today + timedelta(days=7)
    ).count()
    soon = CosmeticProduct.objects.filter(
        expiration_date__gt=today + timedelta(days=7),
        expiration_date__lte=today + timedelta(days=30)
    ).count()
    good = CosmeticProduct.objects.filter(expiration_date__gt=today + timedelta(days=30)).count()
    
    print(f"\nExpiration status statistics:")
    print(f"Expired: {expired} products")
    print(f"Urgent (expiring in 7 days): {urgent} products")
    print(f"Expiring soon (within 30 days): {soon} products")
    print(f"Good status: {good} products")

if __name__ == "__main__":
    create_sample_data()