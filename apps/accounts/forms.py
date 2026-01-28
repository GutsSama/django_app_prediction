from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("email", "first_name", "last_name")

