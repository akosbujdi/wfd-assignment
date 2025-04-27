from django.test import TestCase, Client
from django.urls import reverse
from ..models import CustomUser, Student
from django.utils.timezone import now
from django.contrib.auth.forms import AuthenticationForm


class UserLoginViewTest(TestCase):
    def setUp(self):

        self.user = CustomUser.objects.create_user(
            email='admin@admin.com',
            password='Asdf@123',
            full_name='Test Admin',
        )
        self.student = Student.objects.create(user=self.user)

        self.client = Client()

        self.login_url = reverse('login')

    def test_successful_login(self):
        response = self.client.get(self.login_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

        response = self.client.post(self.login_url, {
            'username': 'admin@admin.com',
            'password': 'Asdf@123',
        })

        self.assertRedirects(response, reverse('home'))

        self.assertTrue('_auth_user_id' in self.client.session)

    def test_unsuccessful_login_invalid_credentials(self):

        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.login_url, {
            'username': 'admin@admin.com',
            'password': 'wrongpassword'
        })

        self.assertTemplateUsed(response, 'login.html')
