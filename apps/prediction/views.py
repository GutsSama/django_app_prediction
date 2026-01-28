from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import PredictionForm
import joblib
import os
import pandas as pd

from django.conf import settings


MODEL_PATH = os.path.join(settings.BASE_DIR, 'apps', 'prediction', 'ml_models', 'insurance_model.joblib')

#class PredictionView(LoginRequiredMixin, FormView):

class PredictionView(FormView):
    template_name = 'predict.html'
    form_class = PredictionForm

    def form_valid(self, form):
        # Charger le modèle
        if os.path.exists(MODEL_PATH):
            self.model = joblib.load(MODEL_PATH)
        else:
            messages.error(self.request, "Le modèle n'a pas été trouvé.")
            return self.render_to_response(self.get_context_data(form=form))

        data = form.cleaned_data
        taille = data['taille'] / 100
        bmi = data['poids'] / (taille ** 2)

        try:
            prediction = self.predict(data, bmi)
            messages.success(self.request, f'Charges estimées : {prediction:.2f} €')
            self.prediction_result = prediction
        except Exception as e:
            messages.error(self.request, f'Erreur : {str(e)}')

        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self, 'prediction_result'):
            context['prediction'] = self.prediction_result
        return context

    def predict(self, data, bmi):
        input_data = pd.DataFrame([{
            'age': data['age'],
            'sex': data['sex'],
            'bmi': bmi,
            'children': data['children'],
            'region': data['region'],
            'smoker' : data['is_fumeur']
        }])

        # Utiliser le modèle chargé
        prediction = self.model.predict(input_data)[0]
        return round(prediction, 2)
