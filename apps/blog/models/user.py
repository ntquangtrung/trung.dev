from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

from model_utils.models import UUIDModel


# Create your models here.
class User(AbstractUser):
    pass

    def __str__(self):
        return f"Username: {self.username}, Email: {self.email}"


class Profile(UUIDModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    year_of_birth = models.PositiveIntegerField(
        blank=True, null=True, help_text="Enter your year of birth"
    )

    def __str__(self):
        return f"Profile of {self.user.username}"

    class Meta:
        verbose_name = "Profile"
