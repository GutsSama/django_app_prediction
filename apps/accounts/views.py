from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView

from .forms import SignupForm, LoginForm, AccountUserForm
from .models import CustomUser, AccountUser

class SignupView(View):
    def get(self, request):
        return render(request, "signup.html", {"form": SignupForm()})

    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # username reste obligatoire en interne -> on le remplit avec l'email
            user.username = user.email
            user.save()
            return redirect("/profile")  # évite ton "/" qui 404
        return render(request, "signup.html", {"form": form})


class LoginView(View):
    def get(self, request):
        return render(request, "login.html", {"form": LoginForm()})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            try:
                u = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                u = None

            user = None
            if u is not None:
                user = authenticate(request, username=u.username, password=password)

            if user:
                login(request, user)
                return redirect("/profile")

            form.add_error(None, "Email ou mot de passe incorrect")

        return render(request, "login.html", {"form": form})


class ProfileView(LoginRequiredMixin, UpdateView):
    model = AccountUser
    form_class = AccountUserForm
    template_name = "profile.html"
    success_url = "/account/profile/"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_conseiller:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        account_user, _ = AccountUser.objects.get_or_create(
            user=self.request.user,
            defaults={
                "is_fumeur": "no",   # valeur valide de tes choices
                "sex": "male",       # optionnel (si sex est aussi NOT NULL chez toi)
                "region": "northeast",  # optionnel
                "children": 0,
            }
        )
        return account_user

