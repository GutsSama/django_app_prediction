from django import forms
from apps.accounts.models import AccountUser


class PredictionForm(forms.ModelForm):
    """Formulaire pour la prédiction"""
    
    class Meta:
        model = AccountUser
        fields = ['age', 'sex', 'taille', 'poids', 'children', 'is_fumeur', 'region']
