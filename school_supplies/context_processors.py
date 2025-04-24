from .models import BasketItem, Basket
from django.db.models import Sum

def basket_count(request):
    if request.user.is_authenticated:
        try:
            basket = Basket.objects.get(user=request.user)
            result = BasketItem.objects.filter(basket=basket).aggregate(total=Sum('quantity'))
            return {'basket_count': result['total'] or 0}
        except Basket.DoesNotExist:
            return {'basket_count': 0}
    return {'basket_count': 0}

