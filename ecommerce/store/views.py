from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product, Order, OrderItem, Customer, ShippingAddress
from django.http import JsonResponse
import json

def store(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'store/store.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    context = {'product': product}
    return render(request, 'store/product_detail.html', context)

def cart(request):
    order, created = Order.objects.get_or_create(complete=False)
    items = order.orderitem_set.all()
    context = {'items': items, 'order': order}
    return render(request, 'store/cart.html', context)

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    if request.method == 'POST':
        # Get the quantity from the form, default to 1 if not a valid number
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity < 1:
                quantity = 1
        except (ValueError, TypeError):
            quantity = 1

        order, created = Order.objects.get_or_create(complete=False)
        order_item, created = OrderItem.objects.get_or_create(order=order, product=product)
        
        # Add the user-specified quantity instead of just 1
        order_item.quantity += quantity
        order_item.save()

        # Send a success message to the user
        messages.success(request, f"Added {quantity} x {product.name} to your cart!")

    return redirect('product_detail', product_id=product.id)

def update_cart_item(request, item_id):
    order_item = get_object_or_404(OrderItem, pk=item_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'increase':
            order_item.quantity += 1
            order_item.save()
        elif action == 'decrease' and order_item.quantity > 1:
            order_item.quantity -= 1
            order_item.save()
    return redirect('cart')

def remove_cart_item(request, item_id):
    order_item = get_object_or_404(OrderItem, pk=item_id)
    if request.method == 'POST':
        order_item.delete()
    return redirect('cart')

def checkout(request):
    order, created = Order.objects.get_or_create(complete=False)
    items = order.orderitem_set.all()
    context = {'items': items, 'order': order}
    return render(request, 'store/checkout.html', context)

def process_order(request):
    data = json.loads(request.body)
    
    order_id = data['order_id']
    order = Order.objects.get(pk=order_id)
    
    shipping_info = data['shipping_info']
    
    # Check if a customer is linked to the order, if not, create one
    if not order.customer:
        customer = Customer.objects.create(name="Guest", email="guest@example.com")
        order.customer = customer
        order.save()
    
    # Mark the order as complete
    order.complete = True
    order.save()
    
    # Create the shipping address
    ShippingAddress.objects.create(
        customer = order.customer,
        order = order,
        address = shipping_info['address'],
        city = shipping_info['city'],
        region = shipping_info['region'],
        zipcode = shipping_info['zipcode']
    )
    
    return JsonResponse('Payment submitted..', safe=False)


def processOrder(request):
    data = json.loads(request.body)
    
    orderId = data['orderId']
    shippingInfo = data['shippingInfo']
    
    order = Order.objects.get(pk=orderId)
    order.complete = True
    order.save()
    
    ShippingAddress.objects.create(
        customer = order.customer,
        order = order,
        address = shippingInfo['address'],
        city = shippingInfo['city'],
        region = shippingInfo['region'],
        zipcode = shippingInfo['zipcode']
    )
    
    return JsonResponse('Payment submitted..', safe=False)
