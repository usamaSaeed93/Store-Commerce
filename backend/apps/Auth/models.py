from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


# Create your models here.
class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **kwargs):
        user = self.model(
            email=email, is_staff=True, is_superuser=True, is_active=True, **kwargs
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractUser):
    email = models.EmailField(max_length=254, unique=True)
    is_verified = models.BooleanField(default=False)
    is_service_provider = models.BooleanField(default=False)
    is_provider_verified = models.BooleanField(default=False)
    username = None
    objects = MyUserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
