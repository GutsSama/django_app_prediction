from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, AccountUser

class SignupForm(UserCreationForm):
    email = forms.EmailField()
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("first_name", "last_name", "email")

class LoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")

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
