from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    is_conseiller = models.BooleanField(default=False)


class AccountUser(models.Model):

    #Faut supprimer null après
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True)


    age = models.PositiveIntegerField(verbose_name="Âge", null=True)
    children = models.PositiveIntegerField(default=0, verbose_name="Nombre d'enfants")

    taille = models.PositiveIntegerField(verbose_name="Taille (cm)",   null=True)
    poids = models.PositiveIntegerField(verbose_name="Poids (kg)",  null=True)

    SEX_CHOICES = (
        ("female", "Femme"),
        ("male", "Homme"),
    )
    sex = models.CharField(choices=SEX_CHOICES, verbose_name="Sexe",  null=True)


    FUMEUR_CHOICES = (
        ("yes", "oui"),
        ("no", "non"),
    )

    is_fumeur = models.CharField(choices=FUMEUR_CHOICES, verbose_name="fumeur",  null=True)


    REGION_CHOICES = [
        ('northeast', 'Nord-Est'),
        ('northwest', 'Nord-Ouest'),
        ('southeast', 'Sud-Est'),
        ('southwest', 'Sud-Ouest'),
    ]
    region = models.CharField(choices=REGION_CHOICES,verbose_name="Région",  null=True)

    def __str__(self):
        return str(self.user) 
