from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import views as auth_views
from django.contrib.auth import authenticate, login, logout
from school_supplies.forms import CustomUserCreationForm, ItemUpdateForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import ItemForm, EditAccountForm
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
                               mark_safe(
                                   f"Only {item.quantity - basket_item.quantity} more of '{item_name}' can be added."))
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
    total_items = sum(item.quantity for item in basket_items)
    subtotal = round(sum(item.item.price * item.quantity for item in basket_items), 2)

    # Initialize discount variables
    discount_rate = 0
    discount_amount = 0
    total = subtotal

    # Check for teacher discount
    if hasattr(request.user, 'teacher') and total_items >= 10:
        discount_rate = request.user.teacher.discount_rate
        discount_amount = round(subtotal * (discount_rate / 100), 2)
        total = subtotal - discount_amount

    if request.method == 'POST':
        for item in basket_items:
            item_name = escape(item.item.name)
            qty_str = request.POST.get(f'quantity_{item.id}', '')
            try:
                new_qty = int(qty_str)
                if new_qty <= 0:
                    item.delete()
                elif new_qty > item.item.quantity:
                    messages.error(request, mark_safe(
                        f"Only {item.item.quantity - item.quantity} of '{item_name}' available in stock."))
                else:
                    messages.success(request, mark_safe(f"'{item_name}' updated in your basket!"))
                    item.quantity = new_qty
                    item.save()
            except ValueError:
                continue

        if not basket.basketitem_set.exists():
            basket.delete()
            return redirect('shop')

        return redirect('view_basket')

    context = {
        'items': basket_items,
        'subtotal': subtotal,
        'total': total,
        'total_items': total_items,
        'discount_applied': discount_rate > 0,
        'discount_rate': discount_rate,
        'discount_amount': discount_amount,
    }
    return render(request, 'view_basket.html', context)


@login_required
@transaction.atomic
def checkout(request):
    basket = Basket.objects.filter(user=request.user).first()
    items = BasketItem.objects.filter(basket=basket)

    if not basket or not items.exists():
        return redirect('shop')

    total_items = sum(item.quantity for item in items)
    subtotal = sum(item.item.price * item.quantity for item in items)

    # Calculate discount if applicable
    discount_rate = 0
    if hasattr(request.user, 'teacher') and total_items >= 10:
        discount_rate = request.user.teacher.discount_rate

    # Apply discount to total
    total_price = subtotal
    if discount_rate > 0:
        total_price = round(subtotal * (1 - discount_rate / 100), 2)

    if request.method == 'POST':
        address = request.POST.get('address')
        eircode = request.POST.get('eircode')

        # Create order with final price (no need to store original/discount separately)
        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            status='Pending'
        )

        # Create shipping info
        ShippingInfo.objects.create(
            order=order,
            address=address,
            eircode=eircode
        )

        # Create order items and update inventory
        for b_item in items:
            OrderItem.objects.create(
                order=order,
                item=b_item.item,
                quantity=b_item.quantity,
                price_at_time=b_item.item.price
            )
            # Update inventory
            b_item.item.quantity -= b_item.quantity
            b_item.item.save()

        # Clear basket
        basket.delete()

        return redirect('order_confirmation')

    context = {
        'items': items,
        'subtotal': subtotal,
        'total_price': total_price,
        'total_items': total_items,
        'discount_applied': discount_rate > 0,
        'discount_rate': discount_rate,
        'discount_amount': subtotal - total_price if discount_rate > 0 else 0,
    }
    return render(request, 'checkout.html', context)


@login_required
def view_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'view_orders.html', {'orders': orders})


@login_required
def edit_account(request):
    user = request.user

    if request.method == 'POST':
        # Get the original full_name before binding the form
        original_full_name = user.full_name
        form = EditAccountForm(request.POST, instance=user)

        if form.is_valid():
            full_name = form.cleaned_data.get('full_name')
            new_password = form.cleaned_data.get('new_password')
            confirm_password = form.cleaned_data.get('confirm_password')

            # Check password mismatch first
            if new_password and new_password != confirm_password:
                form.add_error('confirm_password', 'The passwords do not match.')
                return render(request, 'edit_account.html', {'form': form})

            # Check if nothing changed (compare with original, not current user)
            if full_name == original_full_name and not new_password:
                messages.warning(request, "Nothing has changed.")
                return redirect('edit_account')

            # Proceed with changes if any
            if full_name != original_full_name:
                user.full_name = full_name

            if new_password:
                user.set_password(new_password)

            user.save()
            messages.success(request, "Your account has been updated successfully.")
            return redirect('edit_account')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = EditAccountForm(instance=user)

    return render(request, 'edit_account.html', {'form': form})


@login_required
def inventory_management(request):
    if not request.user.is_inventory_manager():
        return redirect('home')

    items = Item.objects.filter(inv_manage_id=request.user.inventorymanager)

    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        action = request.POST.get('action')

        try:
            item = Item.objects.get(id=item_id, inv_manage_id=request.user.inventorymanager)

            if action == 'update_quantity':  # Quick quantity update
                new_quantity = int(request.POST.get('quantity', 0))
                if new_quantity >= 0:
                    item.quantity = new_quantity
                    item.save()
                    messages.success(request, f"Quantity updated for {item.name}")

            elif action == 'update_full':  # Full form update
                form = ItemUpdateForm(request.POST, request.FILES, instance=item)
                if form.is_valid():
                    form.save()
                    messages.success(request, f"Updated {item.name} details")

        except (Item.DoesNotExist, ValueError):
            messages.error(request, "Invalid operation")

        return redirect('inventory_management')

    return render(request, 'inventory.html', {
        'items': items,
        'form': ItemUpdateForm()  # For full edits
    })


@login_required
def delete_item(request, item_id):
    if not request.user.is_inventory_manager():
        return redirect('home')

    item = get_object_or_404(Item, id=item_id, inv_manage_id=request.user.inventorymanager)
    item.delete()
    messages.success(request, f"Deleted {item.name}")
    return redirect('inventory_management')
