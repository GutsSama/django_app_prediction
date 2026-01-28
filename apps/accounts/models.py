from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class accountUser(models.Model):
    user = models.OneToOneField(User)

    def __str__(self):
        return "Profil de {0}".format(self.user.username)
