from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, AccountUser, CounselorProfile, Appointment
from django.utils import timezone
from datetime import timedelta


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

    first_name = forms.CharField(
        label='Prénom',
        required=True,
        widget=forms.TextInput(attrs={
            "class": "input input-bordered w-full",
            "placeholder": "Votre prénom"
        }),
        error_messages={
            "required": "Le prénom est obligatoire.",
        },
    )

    last_name = forms.CharField(
        label='Nom de famille',
        required=True,
        widget=forms.TextInput(attrs={  
            "class": "input input-bordered w-full",
            "placeholder": "Votre nom de famille"
        }),
        error_messages={
            "required": "Le nom de famille est obligatoire.",
        },
    )

    password1 = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={
            "class": "input input-bordered w-full",
            "placeholder": "Votre mot de passe"
        }),
        help_text="Votre mot de passe doit contenir au moins 8 caractères.",
        error_messages={
            "required": "Le mot de passe est obligatoire.",
        }
    )

    password2 = forms.CharField(
        label='Confirmez le mot de passe',
        widget=forms.PasswordInput(attrs={
            "class": "input input-bordered w-full",
            "placeholder": "Confirmez votre mot de passe"
        }),
        help_text="Entrez le même mot de passe que précédemment, pour vérification.",
        error_messages={
            "required": "La confirmation du mot de passe est obligatoire.",
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
                'placeholder': 'Âge',
                'required': True,
            }),
            'sex': forms.Select(attrs={
                'class': 'select select-bordered w-full',
                'required': True,
            }),
            'taille': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Taille (cm)',
                'required': True,
            }),
            'poids': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Poids (kg)',
                'required': True,
            }),
            'children': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Nombre d\'enfants',
                'required': True,
            }),
            'is_fumeur': forms.Select(attrs={
                'class': 'select select-bordered w-full',
                'required': True,
            }),
            'region': forms.Select(attrs={
                'class': 'select select-bordered w-full',
                'required': True,
            }),
        }
    
    def clean_age(self):
        age = self.cleaned_data.get('age')

        if age is not None:
            if age < 18:
                raise forms.ValidationError("Vous devez avoir au moins 18 ans.")

            if age > 125:
                raise forms.ValidationError("L'âge ne peut pas dépasser 120 ans.")

        return age
    

    def clean_poids(self):
        poids = self.cleaned_data.get('poids')
        if poids is not None:
            if poids < 30:
                raise forms.ValidationError("Le poids semble irréaliste.")
            if poids > 300:
                raise forms.ValidationError("Le poids semble irréaliste.")

        return poids

    def clean_taille(self):
        taille = self.cleaned_data.get('taille')

        if taille is not None:
            if taille < 100 or taille > 250:
                raise forms.ValidationError("La taille doit être comprise entre 100 et 250 cm.")

        return taille

    def clean_children(self):
        children = self.cleaned_data.get('children')

        if children is not None:
            if children > 15:
                raise forms.ValidationError("Valeur trop élevée.")

        return children


    def clean(self):
        cleaned_data = super().clean()

        taille = cleaned_data.get('taille')
        poids = cleaned_data.get('poids')

        if taille is not None and poids is not None:
            taille_m = taille / 100
            bmi = poids / (taille_m ** 2)

            if bmi < 10 or bmi > 60:
                raise forms.ValidationError(
                    "Les valeurs de taille et de poids sont incohérentes."
                )

        return cleaned_data

from django.utils import timezone

class AppointmentForm(forms.Form):
    conseiller = forms.ModelChoiceField(
        queryset=CounselorProfile.objects.all(),
        label="Conseiller",
        empty_label="Choisissez un conseiller",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    appointment_date = forms.DateTimeField(
        label="Date du rendez-vous",
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local', 'class': 'form-control'},
            format='%Y-%m-%dT%H:%M'
        ),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    def clean_conseiller(self):
        conseiller = self.cleaned_data.get('conseiller')
        
        if not conseiller:
            raise forms.ValidationError("Veuillez sélectionner un conseiller.")
        
        return conseiller


    def clean_appointment_date(self):
        date = self.cleaned_data['appointment_date']

        # weekday() : 0=lundi, 6=dimanche
        if date.weekday() >= 5:  # 5=samedi, 6=dimanche
            raise forms.ValidationError("Les rendez-vous ne sont pas disponibles le week-end.")

        # Vérifier si la date du rendez-vous est dans le passé
        if date < timezone.now():
            raise forms.ValidationError("La date du rendez-vous ne peut pas être dans le passé.")
        
        # Vérifier si la date est dans un intervalle de 24 heures
        if date < timezone.now() + timedelta(hours=24):
            raise forms.ValidationError("Le rendez-vous doit être pris au moins 24 heures à l'avance.")

        return date

    
class AppointmentStatusForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'})
        }