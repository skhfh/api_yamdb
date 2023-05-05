from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER_ROLE = 'user'
    MODERATOR_ROLE = 'moderator'
    ADMIN_ROLE = 'admin'
    ROLE_CHOICES = [
        (USER_ROLE, 'User'),
        (MODERATOR_ROLE, 'Moderator'),
        (ADMIN_ROLE, 'Admin'),
    ]
    role = models.CharField(
        'Пользовательская роль',
        max_length=25,
        choices=ROLE_CHOICES,
        default=USER_ROLE,
        blank=True)
    bio = models.TextField(
        'Биография',
        blank=True,
        null=True,
    )

    @property
    def staff_permission(self):
        return (self.role in (self.MODERATOR_ROLE, self.ADMIN_ROLE)
                or self.is_superuser)

    @property
    def admin_permission(self):
        return self.role == self.ADMIN_ROLE or self.is_superuser
