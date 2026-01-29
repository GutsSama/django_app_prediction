from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

from .forms import SignupForm, LoginForm
from .models import CustomUser


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
            return redirect("/login/")  # évite ton "/" qui 404
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
                #return redirect("/admin/")

            form.add_error(None, "Email ou mot de passe incorrect")

        return render(request, "login.html", {"form": form})
