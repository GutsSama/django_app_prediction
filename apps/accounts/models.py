from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    is_conseiller = models.BooleanField(default=False)


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
        ("F", "Femme"),
        ("H", "Homme"),
    )
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, verbose_name="Sexe",  null=True)

    is_fumeur = models.BooleanField(default=False, verbose_name="Fumeur ?")

    REGION_CHOICES = [
        ('northeast', 'Nord-Est'),
        ('northwest', 'Nord-Ouest'),
        ('southeast', 'Sud-Est'),
        ('southwest', 'Sud-Ouest'),
    ]
    region = models.CharField(max_length=10,choices=REGION_CHOICES,verbose_name="Région",  null=True)

    def __str__(self):
        return str(self.user) 

class CounselorProfile(models.Model):
    pass
