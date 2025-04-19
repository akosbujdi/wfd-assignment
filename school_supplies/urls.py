from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Directs to the home view
]