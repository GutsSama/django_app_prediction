from django.test import TestCase
from django.urls import reverse
from apps.accounts.models import CustomUser
from apps.accounts.models import AccountUser


class PredictionViewInitialTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='12345')
        AccountUser.objects.create(
            user=self.user,
            age=30,
            sex='male',
            taille=180,
            poids=75,
            children=2,
            is_fumeur=False,
            region='southeast'
        )
        self.client.login(username='testuser', password='12345')
        self.url = reverse('predict')

    def test_initial_form_values(self):
        response = self.client.get(self.url)
        form = response.context['form']
        self.assertEqual(form.initial['age'], 30)
        self.assertEqual(form.initial['sex'], 'male')
        self.assertEqual(form.initial['poids'], 75)