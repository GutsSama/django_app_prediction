from django import forms
from apps.accounts.models import AccountUser


class PredictionForm(forms.ModelForm):
    """Formulaire pour la prédiction"""
    
    class Meta:
        model = AccountUser
        fields = ['age', 'sex', 'taille', 'poids', 'children', 'is_fumeur', 'region']
        widgets = {
            'age': forms.NumberInput(attrs={
                'class': 'grid input input-neutral',
                'placeholder': 'Âge'
            }),
            'sex': forms.Select(attrs={
                'class': 'grid input input-neutral'
            }),
            'taille': forms.NumberInput(attrs={
                'class': 'input input-neutral',
                'placeholder': 'Taille (cm)'
            }),
            'poids': forms.NumberInput(attrs={
                'class': 'grid input input-neutral',
                'placeholder': 'Poids (kg)'
            }),
            'children': forms.NumberInput(attrs={
                'class': 'grid input input-neutral'
            }),
            'is_fumeur': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-blue-600 focus:ring-blue-500'
            }),
            'region': forms.Select(attrs={
                'class': 'grid input input-neutral'
            }),
        }