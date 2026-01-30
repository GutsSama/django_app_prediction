from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, AccountUser


class SignupForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label='Votre adresse email',
        widget=forms.EmailInput(attrs={
            "class": "input input-bordered w-full",
            "placeholder": "Votre adresse email"
        }),
        error_messages={
            "required": "L'adresse email est obligatoire.",
            "invalid": "Entrez une adresse email valide.",
        },
    )
    
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("email", "first_name", "last_name")
        labels = {
            'email': 'Votre adresse email',
            'first_name': 'Prénom',
            'last_name': 'Nom de famille',
        }
        widgets = {
            "first_name": forms.TextInput(attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Votre prénom"
            }),
            "last_name": forms.TextInput(attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Votre nom de famille"
            }),
        }

class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        required=True,
        label='Votre adresse email',
        widget=forms.EmailInput(attrs={
            "class": "input input-bordered w-full",
            "placeholder": "Entrez votre adresse email"
        }),
        error_messages={
            "required": "L'adresse email est obligatoire.",
            "invalid": "Entrez une adresse email valide.",
        },
    )
    
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={
            "class": "input input-bordered w-full",
            "placeholder": "Votre mot de passe"
        }),
    ))

class AccountUserForm(forms.ModelForm):
    class Meta:
        model = AccountUser
        fields = [
            "age",
            "children",
            "taille",
            "poids",
            "sex",
            "is_fumeur",
            "region",
        ]
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
                'class': 'select select-bordered w-full'
            }),
            'region': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
        }