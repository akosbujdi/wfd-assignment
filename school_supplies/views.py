from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import views as auth_views
from django.contrib.auth import authenticate, login, logout
from school_supplies.forms import CustomUserCreationForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import ItemForm
from .models import Basket, BasketItem, Order, OrderItem, ShippingInfo, Item
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils.html import escape, mark_safe

# Create your views here.
def home(request):
    latest_items = Item.objects.order_by('-id')[:3]
    return render(request, 'home.html', {'latest_items': latest_items})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password")
        else:
            messages.error(request, "Invalid username or password")
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


def add_item_view(request):
    if not request.user.is_authenticated or not hasattr(request.user, 'inventorymanager'):
        return redirect('home')

    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.inv_manage_id = request.user.inventorymanager
            item.save()
            return redirect('shop')
    else:
        form = ItemForm()

    return render(request, 'add_item.html', {'form': form})


def shop_view(request):
    items = Item.objects.all().order_by('-created_at')  # or just .all()
    return render(request, 'shop.html', {'items': items})


@login_required
def add_to_basket(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))

        item = get_object_or_404(Item, id=item_id)
        item_name = escape(item.name)

        if quantity > item.quantity:
            messages.error(request, mark_safe(f"Only {item.quantity} of '{item_name}' available in stock."))
            return redirect('shop')

        basket, created = Basket.objects.get_or_create(user=request.user)

        basket_item, created = BasketItem.objects.get_or_create(
            basket=basket,
            item=item,
            defaults={'quantity': quantity}
        )

        if not created:
            if basket_item.quantity + quantity > item.quantity:
                messages.error(request,
                               mark_safe(f"Only {item.quantity - basket_item.quantity} more of '{item_name}' can be added."))
                return redirect('shop')
            basket_item.quantity += quantity
            basket_item.save()

        messages.success(request, mark_safe(f"'{item_name}' added to your basket!"))
        return redirect('shop')
    return redirect('shop')


@login_required
def order_confirmation(request):
    return render(request, 'order_confirmation.html')


@login_required
def view_basket(request):
    basket, created = Basket.objects.get_or_create(user=request.user)
    basket_items = BasketItem.objects.filter(basket=basket)

    if request.method == 'POST':
        for item in basket_items:
            qty_str = request.POST.get(f'quantity_{item.id}', '')
            try:
                new_qty = int(qty_str)
                if new_qty <= 0:
                    item.delete()
                else:
                    item.quantity = new_qty
                    item.save()
            except ValueError:
                continue

        if not basket.basketitem_set.exists():
            basket.delete()
            return redirect('shop')

        return redirect('view_basket')

    total = round(sum(item.item.price * item.quantity for item in basket_items), 2)

    return render(request, 'view_basket.html', {
        'items': basket_items,
        'total': total,
    })


@login_required
@transaction.atomic
def checkout(request):
    basket = Basket.objects.filter(user=request.user).first()
    items = BasketItem.objects.filter(basket=basket)

    if not basket or not items.exists():
        return redirect('shop')

    total_price = sum(item.item.price * item.quantity for item in items)

    if request.method == 'POST':
        address = request.POST.get('address')
        eircode = request.POST.get('eircode')

        order = Order.objects.create(user=request.user, total_price=total_price)

        ShippingInfo.objects.create(order=order, address=address, eircode=eircode)

        for b_item in items:
            OrderItem.objects.create(
                order=order,
                item=b_item.item,
                quantity=b_item.quantity,
                price_at_time=b_item.item.price
            )
            b_item.item.quantity -= b_item.quantity
            b_item.item.save()

        basket.delete()

        return redirect('order_confirmation')

    return render(request, 'checkout.html', {'items': items, 'total_price': total_price})


@login_required
def view_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'view_orders.html', {'orders': orders})
