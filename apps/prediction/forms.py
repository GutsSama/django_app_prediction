from django import forms
from apps.accounts.models import AccountUser


class PredictionForm(forms.ModelForm):
    """Formulaire pour la prédiction"""
    
    class Meta:
        model = AccountUser
        fields = ['age', 'sex', 'taille', 'poids', 'children', 'is_fumeur', 'region']
        
        labels = {
            'age': 'Âge',
            'sex': 'Sexe',
            'taille': 'Taille',
            'poids': 'Poids',
            'children': 'Nombre d\'enfants',
            'is_fumeur': 'Fumeur ?',
            'region': 'Région',
        }

        widgets = {
            'age': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Âge'
            }),
            'sex': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'taille': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Taille (cm)'
            }),
            'poids': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Poids (kg)'
            }),
            'children': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Nombre d\'enfants'
            }),
            'is_fumeur': forms.Select(attrs={
                'class': 'select select-bordered w-full',
                'choices': [('yes', 'Oui'), ('no', 'Non')]
            }),
            'region': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
        }