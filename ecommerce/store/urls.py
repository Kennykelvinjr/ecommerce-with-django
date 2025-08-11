from django.urls import path
from . import views

urlpatterns = [
	path('', views.store, name="store"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),
	path('update_cart_item/<int:product_id>/<str:action>/', views.update_cart_item, name="update_cart_item"),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name="add_to_cart"),
    path('remove_cart_item/<int:product_id>/', views.remove_cart_item, name="remove_cart_item"), 
	path('process_order/', views.process_order, name="process_order"),
	path('register/', views.register_user, name="register"),
	path('orders/', views.orders, name="orders"),
	path('product/<int:product_id>/', views.product_detail, name="product_detail"),
	path('profile/', views.profile, name="profile"),
    path('create_payment_intent/', views.create_payment_intent, name="create_payment_intent"),
]