from django.test import TestCase, Client
from django.urls import reverse
from ..models import CustomUser, Item, Basket, BasketItem, Student, InventoryManager
from django.utils.timezone import now

class AddToBasketViewTest(TestCase):
    def setUp(self):
        self.inventory_manager_user = CustomUser.objects.create_user(
            email='manager@example.com',
            password='Asdf@123',
            full_name='Inventory Manager'
        )
        self.inventory_manager = InventoryManager.objects.create(user=self.inventory_manager_user)

        self.user = CustomUser.objects.create_user(
            email='teststudent@example.com',
            password='Asdf@123',
            full_name='Test Student'
        )
        self.student = Student.objects.create(user=self.user)

        self.item = Item.objects.create(
            name='Pencil',
            description='A nice pencil',
            price=1.00,
            quantity=10,
            image='items/red-pencil.jpg',
            inv_manage_id=self.inventory_manager,
            created_at=now()
        )

        self.client = Client()
        self.add_to_basket_url = reverse('add_to_basket')

    def test_add_available_item_to_basket(self):
        self.client.login(email='teststudent@example.com', password='Asdf@123')

        response = self.client.post(self.add_to_basket_url, {
            'item_id': self.item.id,
            'quantity': 3,
        })

        self.assertRedirects(response, reverse('shop'))

        basket = Basket.objects.get(user=self.user)
        basket_item = BasketItem.objects.get(basket=basket, item=self.item)

        self.assertEqual(basket_item.quantity, 3)

        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("added to your basket" in str(message) for message in messages))

