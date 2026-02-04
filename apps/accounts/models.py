from django.db import models
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

    age = models.PositiveIntegerField(verbose_name="Âge")
    children = models.PositiveIntegerField(default=0, verbose_name="Nombre d'enfants")

    taille = models.PositiveIntegerField(verbose_name="Taille (cm)")
    poids = models.PositiveIntegerField(verbose_name="Poids (kg)")
    SEX_CHOICES = (
        ("female", "Femme"),
        ("male", "Homme"),
    )
    sex = models.CharField(choices=SEX_CHOICES, verbose_name="Sexe", default='male')


    FUMEUR_CHOICES = (
        ("yes", "oui"),
        ("no", "non"),
    )

    is_fumeur = models.CharField(choices=FUMEUR_CHOICES, verbose_name="fumeur", default="no")


    REGION_CHOICES = [
        ('northeast', 'Nord-Est'),
        ('northwest', 'Nord-Ouest'),
        ('southeast', 'Sud-Est'),
        ('southwest', 'Sud-Ouest'),
    ]
    region = models.CharField(choices=REGION_CHOICES,verbose_name="Région", default="northeast")

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
        choices=[('pending', 'En attente'), ('confirmed', 'Confirmé'), ('completed', 'Terminé')],
        default='pending',
        max_length=20,
        verbose_name="Statut"
    )
    
    def __str__(self):
        return f"Rendez-vous de {self.client.username} avec {self.conseiller.user.username} à {self.appointment_date}"

    def is_past_due(self):
        return self.appointment_date < timezone.now() and self.status != 'completed'
