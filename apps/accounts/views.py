from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.views.generic import UpdateView
from django.urls import reverse_lazy

from .forms import SignupForm, LoginForm, AccountUserForm
from .models import AccountUser
from django.contrib import messages
class SignupView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("/accueil")
        return super().dispatch(request, *args, **kwargs)
    def get(self, request):
        return render(request, "signup.html", {"form": SignupForm()})

    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email
            user.save()
            login(request, user)
            messages.success(request, "Inscription réussie. Vous êtes maintenant connecté.")
            return redirect("/profile")
        return render(request, "signup.html", {"form": form})

class CustomLoginView(LoginView):
    template_name = "login.html"
    authentication_form = LoginForm
    success_url = "/accueil"

    def form_valid(self, form):
        messages.success(self.request, "Vous êtes maintenant connecté.")
        return super().form_valid(form)
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("/accueil")
        return super().dispatch(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, UpdateView):
    model = AccountUser
    form_class = AccountUserForm
    template_name = "profile.html"
    success_url = reverse_lazy("profile")

    def form_valid(self, form):
        messages.success(self.request, "Votre profil a été mis à jour avec succès.")
        return super().form_valid(form)
    

    def dispatch(self, request, *args, **kwargs):
        if  request.user.is_authenticated and request.user.is_conseiller:
            return redirect("/accueil")
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        account_user, _ = AccountUser.objects.get_or_create(
            user=self.request.user,
            defaults={
                "is_fumeur": "no",
                "sex": "male",
                "region": "northeast",
                "children": 0,
            }
        )
        return account_user