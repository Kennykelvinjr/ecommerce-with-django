from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name="store"),
    path('product/<int:product_id>/', views.product_detail, name="product_detail"),
    path('cart/', views.cart, name="cart"),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name="add_to_cart"),
    path('update-cart-item/<int:item_id>/', views.update_cart_item, name="update_cart_item"),
    path('remove-cart-item/<int:item_id>/', views.remove_cart_item, name="remove_cart_item"),
    path('checkout/', views.checkout, name="checkout"),
    path('process_order/', views.process_order, name="process_order"),
]