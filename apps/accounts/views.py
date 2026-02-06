from django.views import View
"""
Module for handling user authentication, profile management, and appointment scheduling.
This module provides views for user signup, login, profile updates, and appointment
management for both clients and counselors in a Django prediction application.
Classes:
    SignupView: Handles user registration and account creation.
    CustomLoginView: Custom login view with redirect and message handling.
    ProfileView: Manages user profile updates for non-counselor users.
    AppointmentView: Handles appointment creation and viewing for clients.
    CounselorAppointmentsView: Manages appointment status updates for counselors.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from .forms import SignupForm, LoginForm, AccountUserForm, AppointmentForm, AppointmentStatusForm
from .models import AccountUser, Appointment, CounselorProfile
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

class SignupView(View):
    """
    View class for user registration/signup functionality.

    This view handles the user signup process with the following features:
    - Redirects authenticated users to the home page
    - Displays the signup form on GET requests
    - Processes form submission and creates new user accounts on POST requests
    - Sets the user's username to their email address
    - Automatically logs in the user after successful registration
    - Displays success message upon completion

    Attributes:
        None

    Methods:
        dispatch: Checks if user is authenticated and redirects if true
        get: Renders the signup form template
        post: Validates and processes the signup form, creates user account, and logs them in
    """
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
    """
    Custom login view that extends Django's built-in LoginView.
    This view handles user authentication with custom form validation,
    success message feedback, and automatic redirection for already
    authenticated users.
    Attributes:
        template_name (str): The template used to render the login form.
        authentication_form (Form): Custom login form class for authentication.
    Methods:
        get_success_url(): Returns the redirect URL after successful login.
        form_valid(form): Handles successful form submission with user feedback messages.
        dispatch(request, *args, **kwargs): Prevents authenticated users from accessing the login page.
    """
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
    """
    View for managing user profile updates.
    A class-based view that allows authenticated users to view and update their profile information.
    Redirects conseiller (advisor) users to the home page. Automatically creates an AccountUser
    instance with default values if one doesn't exist for the current user.
    Attributes:
        model: The AccountUser model used for this view
        form_class: AccountUserForm for handling profile data
        template_name: The template used to render the profile page
        success_url: URL to redirect to after successful form submission
    Methods:
        form_valid(form): Displays a success message after profile update
        dispatch(request, *args, **kwargs): Redirects conseiller users away from this view
        get_object(queryset): Retrieves or creates an AccountUser for the current user with default settings
    """
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
    login_url = '/login/'
    redirect_field_name = 'next'

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

            # Vérification si la date du rendez-vous est dans le passé
            if appointment_date < timezone.now():
                messages.error(request, "La date du rendez-vous ne peut pas être dans le passé.")
                return render(request, self.template_name, {"form": form})

            # Vérification si la date du rendez-vous est trop proche (moins de 24 heures)
            if appointment_date < timezone.now() + timedelta(hours=24):
                messages.error(request, "Le rendez-vous doit être pris au moins 24 heures à l'avance.")
                return render(request, self.template_name, {"form": form})

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
            # Si le formulaire n'est pas valide, réafficher le formulaire avec les erreurs
            return render(request, self.template_name, {"form": form})


class AppointmentView(LoginRequiredMixin, View):
    template_name = "appointments.html"
    login_url = '/login/'
    redirect_field_name = 'next'

    def dispatch(self, request, *args, **kwargs):
        # Empêcher les conseillers d'accéder à cette page
        

        if not request.user.is_authenticated:
            return self.handle_no_permission()

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
        

class CounselorAppointmentsView(LoginRequiredMixin, View):
    """
    View for managing counselor appointments.

    This view allows authenticated counselors to view and update the status of their appointments.
    Only users with counselor role (is_conseiller=True) can access this view.

    Attributes:
        template_name (str): The template used to render the counselor appointments page.

    Methods:
        dispatch: Verifies that the user has counselor permissions before processing the request.
        get: Retrieves all appointments associated with the counselor and displays them with forms.
        post: Updates the status of a specific appointment.

    Raises:
        Http404: If the appointment doesn't belong to the logged-in counselor.
        CounselorProfile.DoesNotExist: If the user's counselor profile is not configured.
    """
    template_name = "counselor_appointments.html"
    login_url = '/login/'
    redirect_field_name = 'next'

    def dispatch(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not request.user.is_conseiller:
            messages.error(request, "Accès réservé aux conseillers.")
            return redirect("/accueil")
        
        return super().dispatch(request, *args, **kwargs)
        
    def get(self, request):
        try:
            counselor_profile = request.user.profile
        except CounselorProfile.DoesNotExist:
            messages.error(request, "Votre profil conseiller n'est pas configuré.")
            return redirect("/accueil")

        # Récupère tous les rendez-vous liés à ce conseiller
        appointments = Appointment.objects.filter(conseiller=counselor_profile).order_by('appointment_date')

        # Prépare un formulaire par rendez-vous
        appointment_forms = []
        for appt in appointments:
            form = AppointmentStatusForm(instance=appt)
            appointment_forms.append((appt, form))

        return render(request, self.template_name, {
            'appointment_forms': appointment_forms
        })

    def post(self, request):
        appointment_id = request.POST.get('appointment_id')
        if not appointment_id:
            messages.error(request, "Aucun rendez-vous sélectionné.")
            return redirect("/my-appointments")

        # Vérifie que le rendez-vous appartient bien au conseiller connecté
        appointment = get_object_or_404(
            Appointment,
            id=appointment_id,
            conseiller__user=request.user
        )

        form = AppointmentStatusForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, "Le statut du rendez-vous a été mis à jour.")
        else:
            messages.error(request, "Erreur lors de la mise à jour du statut.")

        return redirect("/my-appointments")