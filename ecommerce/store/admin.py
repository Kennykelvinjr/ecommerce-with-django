from django.contrib import admin
from .models import Customer, OrderItem, Product, ShippingAddress, Order


admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Customer)
admin.site.register(ShippingAddress)