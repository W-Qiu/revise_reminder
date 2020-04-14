from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(email = self.normalize_email(email))
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email = self.normalize_email(email))
        user.is_admin = True
        user.set_password(password)
        user.save()
        return user

class CustomUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    preset_target = models.IntegerField(default=20)
    today_progress = models.IntegerField(default=0)

    # strategy choices
    STRATEGY_CHOICES = [
        ('forgetting curve', 'forgetting curve'),
        ('by last test date', 'by last test date'),
    ]
    revise_strategy = models.TextField(choices=STRATEGY_CHOICES,
                                        default='forgetting curve')

    objects = CustomUserManager()

    # Required to work with admin
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # Required by AbstractBaseUser
    USERNAME_FIELD = 'email'  # unique identifier for auth backend
    REQUIRED_FIELDS = []

    # Required to work with admin
    def has_perm(self, perm, obj=None):
        return self.is_admin

    # Required to work with admin
    def has_module_perms(self, app_label):
        return self.is_admin

    # Required to work with admin
    def is_staff(self):
        return self.is_admin