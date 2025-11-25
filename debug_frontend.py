#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from myapp.models import CosmeticProduct
from myapp.views import CosmeticProductListView

def debug_frontend():
    print("=== 前端数据显示问题诊断 ===\n")
    
    # 1. 检查数据
    print("1. 数据库数据检查:")
    print(f"   总产品数: {CosmeticProduct.objects.count()}")
    
    users = User.objects.all()
    for user in users:
        count = CosmeticProduct.objects.filter(user=user).count()
        print(f"   用户 '{user.username}': {count} 个产品")
    
    # 2. 模拟视图请求
    print("\n2. 视图测试:")
    factory = RequestFactory()
    
    # 获取第一个用户
    if users.exists():
        user = users.first()
        request = factory.get('/myapp/')
        request.user = user
        
        # 测试视图
        view = CosmeticProductListView()
        view.request = request
        queryset = view.get_queryset()
        
        print(f"   视图返回的产品数: {queryset.count()}")
        
        # 测试模板上下文
        view.object_list = queryset
        context = view.get_context_data()
        print(f"   模板上下文中的产品数: {len(context['products'])}")
    
    # 3. 检查模板文件
    print("\n3. 模板文件检查:")
    template_path = 'myapp/templates/myapp/product_list.html'
    if os.path.exists(template_path):
        with open(template_path, 'r') as f:
            content = f.read()
            has_products_loop = '{% for product in products %}' in content
            print(f"   模板文件存在: 是")
            print(f"   包含产品循环: {'是' if has_products_loop else '否'}")
    else:
        print(f"   模板文件存在: 否")
    
    print("\n4. 建议:")
    if CosmeticProduct.objects.count() == 0:
        print("   ❌ 数据库中没有产品数据")
        print("   💡 运行: python manage.py shell 创建测试数据")
    else:
        print("   ✅ 数据库中有数据")
        print("   💡 检查模板变量名和视图中的context_object_name是否匹配")

if __name__ == "__main__":
    debug_frontend()