from django.urls import path, re_path
from . import views

urlpatterns = [
    path('promocodes/', views.promocode_list_view, name='promocodes'),
    path('promocodes/create/', views.promocode_create, name='promocode_create'),
    path('promocodes/edit/<int:id>/', views.promocode_edit, name='promocode_edit'),
    path('promocodes/delete/<int:id>/', views.promocode_delete, name='promocode_delete'),
    
    # Корзина
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart_view, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart_view, name='remove_from_cart'),
    path('cart/update/<int:product_id>/', views.update_cart_view, name='update_cart'),

    # Оформление заказа и админка
    path('checkout/', views.checkout_view, name='checkout'),
    re_path(r'^order/(?P<pk>[0-9]+)/$', views.order_detail_view, name='order_detail'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
]