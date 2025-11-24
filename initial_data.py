from django.contrib.auth.models import User
from myapp.models import Brand, Category, CosmeticProduct, UsageLog
from datetime import date, timedelta
import random

# 创建测试用户
user, created = User.objects.get_or_create(username='testuser')
if created:
    user.set_password('testpass123')
    user.save()

# 创建品牌
brands_data = [
    "L'Oréal", "Maybelline", "Estée Lauder", "MAC", "NARS", 
    "Fenty Beauty", "Glossier", "The Ordinary", "La Roche-Posay", "CeraVe"
]
brands = []
for brand_name in brands_data:
    brand, created = Brand.objects.get_or_create(name=brand_name)
    brands.append(brand)
    print(f"Created brand: {brand_name}")

# 创建分类
categories_data = {
    'skincare': ['Cleanser', 'Moisturizer', 'Serum', 'Sunscreen', 'Toner'],
    'makeup': ['Foundation', 'Lipstick', 'Mascara', 'Eyeshadow', 'Blush'],
    'fragrance': ['Perfume', 'Cologne', 'Body Spray'],
    'hair': ['Shampoo', 'Conditioner', 'Hair Mask', 'Hair Oil'],
    'body': ['Body Lotion', 'Body Wash', 'Hand Cream']
}

categories = []
for cat_type, cat_names in categories_data.items():
    for cat_name in cat_names:
        category, created = Category.objects.get_or_create(
            name=cat_name, 
            category_type=cat_type
        )
        categories.append(category)
        print(f"Created category: {cat_name} ({cat_type})")

# 创建化妆品产品
product_names = [
    "Hydrating Moisturizer", "Matte Lipstick", "Volumizing Mascara", 
    "Anti-Aging Serum", "SPF 50 Sunscreen", "Foundation Stick",
    "Nourishing Shampoo", "Repairing Conditioner", "Eau de Parfum",
    "Gentle Cleanser", "Brightening Toner", "Cream Blush",
    "Eye Cream", "Face Oil", "Setting Powder", "Liquid Eyeliner",
    "Brow Pencil", "Face Mask", "Body Butter", "Hand Cream"
]

status_options = ['unopened', 'opened', 'finished', 'discarded']

for i, product_name in enumerate(product_names):
    # 随机选择品牌和分类
    brand = random.choice(brands)
    category = random.choice(categories)
    
    # 随机生成日期
    purchase_date = date.today() - timedelta(days=random.randint(0, 365))
    expiration_date = purchase_date + timedelta(days=random.randint(30, 720))
    
    # 随机状态
    status = random.choice(status_options)
    opened_date = None
    if status == 'opened':
        opened_date = purchase_date + timedelta(days=random.randint(0, 100))
    
    # 创建产品
    product = CosmeticProduct.objects.create(
        name=product_name,
        brand=brand,
        category=category,
        user=user,
        shade=random.choice(["", "Ivory", "Beige", "Natural", "Warm", "Cool"]),
        capacity=random.choice(["30ml", "50ml", "100ml", "15g", "5oz"]),
        purchase_date=purchase_date,
        price=round(random.uniform(5, 100), 2),
        purchase_location=random.choice(["Sephora", "Ulta", "Department Store", "Online"]),
        expiration_date=expiration_date,
        status=status,
        opened_date=opened_date,
        pao_after_opening=random.choice([6, 12, 18, 24]),
        rating=random.choice([None, 1, 2, 3, 4, 5]),
        description=f"Sample description for {product_name}",
        ingredients="Aqua, Glycerin, etc.",
        notes=random.choice(["", "Love this product!", "Will repurchase", "Not for me"])
    )
    print(f"Created product: {product.name}")

# 为部分产品创建使用记录
opened_products = CosmeticProduct.objects.filter(status='opened')
for product in opened_products[:5]:  # 只为前5个已开封产品创建记录
    for j in range(random.randint(1, 5)):
        UsageLog.objects.create(
            product=product,
            notes=random.choice([
                "Great product!",
                "Works well for my skin type",
                "Nice texture",
                "Will buy again",
                "Not sure about this one"
            ])
        )
    print(f"Created usage logs for: {product.name}")

print("Data population completed!")