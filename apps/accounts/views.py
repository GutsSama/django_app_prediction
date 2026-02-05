from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.views.generic import UpdateView
from django.urls import reverse_lazy

from .forms import SignupForm, LoginForm, AccountUserForm, AppointmentForm
from .models import AccountUser, Appointment, CounselorProfile
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

    def get_success_url(self):
        """Redirige toujours vers /accueil après login"""
        return "/accueil"
    
    def form_valid(self, form):
        is_valid = super().form_valid(form)
        if is_valid:
            messages.success(self.request, "Vous êtes maintenant connecté.")
        else:
            messages.error(self.request, "Échec de la connexion. Veuillez vérifier vos identifiants.")
        return is_valid
    
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
        is_valid = super().form_valid(form)
        if is_valid:
            messages.success(self.request, "Votre profil a été mis à jour avec succès.")
        return is_valid
    

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

class AppointmentView(LoginRequiredMixin, View):
    template_name = "appointments.html"

    def dispatch(self, request, *args, **kwargs):
        # Empêcher les conseillers d'accéder à cette page
        
        if request.user.is_conseiller:
            return redirect("/accueil")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        # Vérifie si l'utilisateur a déjà un rendez-vous
        if Appointment.objects.filter(client=request.user).exists():
            user_appointments = Appointment.objects.filter(client=request.user)
            return render(request, self.template_name, {
                'user_appointments': user_appointments
            })
        else:
            form = AppointmentForm()
            return render(request, self.template_name, {"form": form})

    def post(self, request):
        # Empêche la création d'un second rendez-vous
        if Appointment.objects.filter(client=request.user).exists():
            messages.error(request, "Vous avez déjà un rendez-vous. Un seul est autorisé.")
            return redirect("/appointments")

        form = AppointmentForm(request.POST)
        if form.is_valid():
            conseiller = form.cleaned_data['conseiller']
            appointment_date = form.cleaned_data['appointment_date']

            # Assigner le conseiller si ce n'est pas déjà fait
            if not request.user.conseiller:
                request.user.conseiller = conseiller
                request.user.save()

            # Créer le rendez-vous
            Appointment.objects.create(
                client=request.user,
                conseiller=conseiller,
                appointment_date=appointment_date,
                status='pending'
            )
            messages.success(request, "Votre rendez-vous a été créé avec succès.")
            return redirect("/appointments")
        else:
            # Réaffiche le formulaire avec erreurs (ex: date invalide)
            return render(request, self.template_name, {"form": form})