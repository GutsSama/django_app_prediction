from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
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
    )

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
    
    def clean_age(self):
        age = self.cleaned_data.get('age')

        if age < 18:
            raise forms.ValidationError("Vous devez avoir au moins 18 ans.")

        if age > 125:
            raise forms.ValidationError("L’âge ne peut pas dépasser 120 ans.")

        return age
    

    def clean_poids(self):
        poids = self.cleaned_data.get('poids')

        if poids > 300:
            raise forms.ValidationError("Le poids semble irréaliste.")

        return poids

    def clean_taille(self):
        taille = self.cleaned_data.get('taille')

        if taille < 100 or taille > 250:
            raise forms.ValidationError("La taille doit être comprise entre 100 et 250 cm.")

        return taille

    def clean_children(self):
        children = self.cleaned_data.get('children')

        if children > 15:
            raise forms.ValidationError("Valeur trop élevée.")

        return children


    def clean(self):
        cleaned_data = super().clean()

        taille = cleaned_data.get('taille')
        poids = cleaned_data.get('poids')

        if taille and poids:
            taille_m = taille / 100
            bmi = poids / (taille_m ** 2)

            if bmi < 10 or bmi > 60:
                raise forms.ValidationError(
                    "Les valeurs de taille et de poids sont incohérentes."
                )

        return cleaned_data

from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class UserNameForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name")
        widgets = {
            "first_name": forms.TextInput(attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Prénom"
            }),
            "last_name": forms.TextInput(attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Nom"
            }),
        }
