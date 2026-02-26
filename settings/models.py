from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ("Admin", "Admin"),
        ("DataEntry", "Data Entry"),
        ("Viewer", "Viewer"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="Viewer")
