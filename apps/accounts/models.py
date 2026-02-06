from django.db import models
"""
Models for user accounts, counselor profiles, and appointment management.
This module defines the core data models for a Django application that manages
custom user accounts with different roles (regular users and counselors/advisors),
user profile information, and appointment scheduling between clients and counselors.
Classes:
    CustomUser: Extended Django user model with additional fields for counselor
                status and assignment to a counselor.
    AccountUser: User profile model storing personal and demographic information
                 including age, physical measurements, gender, smoking status,
                 and regional location.
    CounselorProfile: Profile model for users with counselor/advisor role,
                      containing descriptive information.
    Appointment: Model representing scheduled appointments between clients
                 and counselors with status tracking and validation.
"""
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class CustomUser(AbstractUser):
    is_conseiller = models.BooleanField(default=False)
    email = models.EmailField(unique=True)
    conseiller = models.ForeignKey(
        'CounselorProfile',  # Lier à un conseiller (seul un conseiller peut être affecté à un utilisateur)
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clients',  # Permet de récupérer tous les clients associés à un conseiller
        verbose_name="Conseiller"
    )


class AccountUser(models.Model):

    user = models.OneToOneField(
    CustomUser,
    on_delete=models.CASCADE,
    related_name="account_profile"
    )

    age = models.PositiveIntegerField(verbose_name="Âge", null=True)
    children = models.PositiveIntegerField(default=0, verbose_name="Nombre d'enfants")

    taille = models.PositiveIntegerField(verbose_name="Taille (cm)",   null=True)
    poids = models.PositiveIntegerField(verbose_name="Poids (kg)",  null=True)

    SEX_CHOICES = (
        ("female", "Femme"),
        ("male", "Homme"),
    )
    sex = models.CharField(choices=SEX_CHOICES, verbose_name="Sexe",  null=True, default='male')


    FUMEUR_CHOICES = (
        ("yes", "oui"),
        ("no", "non"),
    )

    is_fumeur = models.CharField(choices=FUMEUR_CHOICES, verbose_name="fumeur",  null=True, default="no")


    REGION_CHOICES = [
        ('northeast', 'Nord-Est'),
        ('northwest', 'Nord-Ouest'),
        ('southeast', 'Sud-Est'),
        ('southwest', 'Sud-Ouest'),
    ]
    region = models.CharField(choices=REGION_CHOICES,verbose_name="Région",  null=True,   default="northeast")

    def __str__(self):
        return str(self.user) 

class CounselorProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='profile', 
        verbose_name="Utilisateur"
    )
    description = models.TextField(null=True, blank=True, verbose_name="Description du conseiller")
    
    def __str__(self):
        return f"Conseiller: {self.user.username}"

class Appointment(models.Model):
    client = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='appointments',
        verbose_name="Client"
    )
    conseiller = models.ForeignKey(
        CounselorProfile, 
        on_delete=models.CASCADE, 
        related_name='appointments',
        verbose_name="Conseiller"
    )
    appointment_date = models.DateTimeField(verbose_name="Date du rendez-vous")
    status = models.CharField(
        choices=[('pending', 'En attente'), ('confirmed', 'Confirmé'), ('completed', 'Terminé'), ('canceled', 'Annulé')],
        default='pending',
        max_length=20,
        verbose_name="Statut"
    )
    
    def __str__(self):
        return f"Rendez-vous de {self.client.username} avec {self.conseiller.user.username} à {self.appointment_date}"

    def is_past_due(self):
        return self.appointment_date < timezone.now() and self.status not in ['completed', 'canceled']
