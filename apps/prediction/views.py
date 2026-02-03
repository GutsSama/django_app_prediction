from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import PredictionForm
from .services import predict
from django.conf import settings
from apps.accounts.models import AccountUser


class PredictionView(LoginRequiredMixin, FormView):
   
    template_name = 'predict.html'
    form_class = PredictionForm
    success_url = reverse_lazy('predict')
    login_url = '/login/'


    def get_initial(self):
        initial = super().get_initial()
       
        try:
            account = AccountUser.objects.get(user=self.request.user)
            initial = {
                'age': account.age,
                'sex': account.sex,
                'taille': account.taille,
                'poids': account.poids,
                'children': account.children,
                'is_fumeur': account.is_fumeur,
                'region': account.region,
            }
        except AccountUser.DoesNotExist:
            pass
       
        return initial


    def form_valid(self, form):

        data = form.cleaned_data
        taille = data['taille'] / 100
        bmi = data['poids'] / (taille ** 2)

        try:
            prediction = predict(data, bmi)
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