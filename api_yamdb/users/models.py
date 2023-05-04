from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(
        'Пользовательская роль',
        max_length=25,
        choices=ROLE_CHOICES,
        default='user',
        blank=True)
    bio = models.TextField(
        'Биография',
        blank=True,
        null=True,
    )

    @property
    def staff_permission(self):
        return self.role in ('moderator', 'admin') or self.is_superuser

    @property
    def admin_permission(self):
        return self.role == 'admin' or self.is_superuser
