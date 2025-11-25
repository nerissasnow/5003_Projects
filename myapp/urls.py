from django.urls import path
from . import views

app_name = 'myapp'

urlpatterns = [
    path('', views.CosmeticProductListView.as_view(), name='product_list'),
    path('add/', views.CosmeticProductCreateView.as_view(), name='product_add'),
    path('<int:pk>/', views.CosmeticProductDetailView.as_view(), name='product_detail'),
    path('<int:pk>/edit/', views.CosmeticProductUpdateView.as_view(), name='product_edit'),
    path('expiring/', views.ExpiringProductsView.as_view(), name='expiring_products'), 
    path('<int:pk>/delete/', views.CosmeticProductDeleteView.as_view(), name='product_delete'),
]