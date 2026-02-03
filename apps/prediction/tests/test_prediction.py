from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, Mock
from apps.accounts.models import CustomUser


class PredictionGeneratedInContextTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        self.valid_form_data = {
            'age': 30,
            'sex': 'male',
            'taille': 175,
            'poids': 75,
            'children': 2,
            'is_fumeur': 'no',
            'region': 'northeast'
        }
    
    @patch('apps.prediction.views.load_model')
    def test_prediction_exists_in_context(self, mock_load_model):
        
        mock_model = Mock()
        mock_model.predict.return_value = [1234.56]
        mock_load_model.return_value = mock_model
        
        response = self.client.post(reverse('predict'), data=self.valid_form_data)
        
        self.assertIn('prediction', response.context)

    
    @patch('apps.prediction.views.load_model')
    def test_prediction_is_numeric(self, mock_load_model):
            
        mock_model = Mock()
        mock_model.predict.return_value = [5678.90]
        mock_load_model.return_value = mock_model
            
        response = self.client.post(reverse('predict'), data=self.valid_form_data)
            
        self.assertIn('prediction', response.context)
            
        prediction = response.context['prediction']
        self.assertIsInstance(prediction, (int, float))