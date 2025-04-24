from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import views as auth_views
from django.contrib.auth import authenticate, login, logout
from school_supplies.forms import CustomUserCreationForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import ItemForm
from .models import Item, Basket, BasketItem
from django.contrib.auth.decorators import login_required


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
        basket, created = Basket.objects.get_or_create(user=request.user)

        basket_item, created = BasketItem.objects.get_or_create(
            basket=basket,
            item=item,
            defaults={'quantity': quantity}
        )

        if not created:
            basket_item.quantity += quantity
            basket_item.save()

        return redirect('shop')


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

    items = [(item, round(item.item.price * item.quantity, 2)) for item in basket_items]
    total = round(sum(sub for _, sub in items), 2)

    return render(request, 'view_basket.html', {
        'items': items,
        'total': total,
    })
