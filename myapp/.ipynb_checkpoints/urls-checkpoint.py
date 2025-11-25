from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'myapp'

urlpatterns = [
    path('', views.CosmeticProductListView.as_view(), name='product_list'),
    path('add/', views.CosmeticProductCreateView.as_view(), name='product_add'),
    path('<int:pk>/', views.CosmeticProductDetailView.as_view(), name='product_detail'),
    path('<int:pk>/edit/', views.CosmeticProductUpdateView.as_view(), name='product_edit'),
    path('expiring/', views.ExpiringProductsView.as_view(), name='expiring_products'), 
    path('<int:pk>/delete/', views.CosmeticProductDeleteView.as_view(), name='product_delete'),
    path('<int:pk>/', views.CosmeticProductDetailView.as_view(), name='product_detail_by_id'),
    # 添加退出登录路由
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    # 登录路由（如果还没有）
    path('login/', auth_views.LoginView.as_view(template_name='myapp/login.html'), name='login'),
]