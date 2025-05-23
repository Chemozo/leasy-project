from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = "email"       # Autenticar con email
    REQUIRED_FIELDS = ["username"]  # username aún requerido para createsuperuser

    def __str__(self):
        return self.email
