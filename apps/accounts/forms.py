from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class SignupForm(UserCreationForm):
    email = forms.EmailField()
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("email", "first_name", "last_name")


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    # accounts/forms.py
from django import forms
from .models import AccountUser

# accounts/forms.py
from django import forms
from .models import AccountUser

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
