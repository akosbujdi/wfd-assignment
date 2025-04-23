from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views
from django.contrib.auth import authenticate, login, logout
from school_supplies.forms import CustomUserCreationForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import ItemForm
from .models import Item


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
