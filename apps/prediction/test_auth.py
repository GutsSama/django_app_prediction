from django.test import TestCase
from django.urls import reverse
from apps.accounts.models import CustomUser 

class PredictionViewAccessTest(TestCase):

    def setUp(self):
        self.url = reverse('predict')
        self.user = CustomUser.objects.create_user(username='testuser', password='12345')

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f'/login/?next={self.url}')

    def test_logged_in_user_access(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'predict.html')
