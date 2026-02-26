from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = [
        ("Admin", "Admin"),
        ("DataEntry", "Data Entry"),
        ("Viewer", "Viewer"),
    ]

    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("username", "email", "role")  # include role


class CustomUserChangeForm(UserChangeForm):
    ROLE_CHOICES = [
        ("Admin", "Admin"),
        ("DataEntry", "Data Entry"),
        ("Viewer", "Viewer"),
    ]

    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "role", "is_active", "is_staff")
