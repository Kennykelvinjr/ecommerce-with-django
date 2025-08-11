from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Product, Order, OrderItem, Customer, ShippingAddress
from django.http import JsonResponse
import json
from .forms import UserUpdateForm, ProfileUpdateForm
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
def create_payment_intent(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            total = data.get('total', 0)

            intent = stripe.PaymentIntent.create(
                amount=int(total * 100),
                currency='usd',
                payment_method_types=['card'],
            )
            return JsonResponse({'clientSecret': intent.client_secret})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def store(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'store/store.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    context = {'product': product}
    return render(request, 'store/product_detail.html', context)

def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        # For non-logged-in users, provide an empty cart
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}

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

        # Get the customer for the logged-in user
        customer = request.user.customer
        
        # Get or create the order for the specific customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        order_item, created = OrderItem.objects.get_or_create(order=order, product=product)
        
        # Add the user-specified quantity instead of just 1
        order_item.quantity += quantity
        order_item.save()

        # Send a success message to the user
        messages.success(request, f"Added {quantity} x {product.name} to your cart!")

    return redirect('product_detail', product_id=product.id)

def update_cart_item(request, product_id, action):
    customer = request.user.customer
    product = Product.objects.get(id=product_id)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

def remove_cart_item(request, item_id):
    order_item = get_object_or_404(OrderItem, pk=item_id)
    if request.method == 'POST':
        order_item.delete()
    return redirect('cart')


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}

    context = {'items': items, 'order': order, 'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY}
    return render(request, 'store/checkout.html', context)


def process_order(request):
    if request.method == 'POST':
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')

        if request.user.is_authenticated:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=address,
                phone_number=phone_number
            )
            order.complete = True
            order.save()
            return redirect('store')
        
    return redirect('checkout')


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


def register_user(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')
    context = {'form': form}
    return render(request, 'store/register.html', context)


@login_required(login_url='login')
def orders(request):
    customer, created = Customer.objects.get_or_create(user=request.user)
    orders = Order.objects.filter(customer=customer, complete=True).order_by('-date_ordered')
    context = {'orders': orders}
    return render(request, 'store/orders.html', context)


@login_required(login_url='login')
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'store/profile.html', context)


def remove_cart_item(request, product_id):
    customer = request.user.customer
    product = Product.objects.get(id=product_id)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if orderItem:
        orderItem.delete()

    return JsonResponse('Item was removed', safe=False)