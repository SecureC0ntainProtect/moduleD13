from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class MyUser(AbstractUser):
    """User model."""
    username = models.CharField(max_length=20)
    enabled = models.BooleanField(default=False)
    email = models.EmailField('email address', unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
