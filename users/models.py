from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, nick, password=None):
        if not nick:
            raise ValueError('Users must have a nickname')
        user = self.model(nick=nick)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, nick, password):
        user = self.create_user(nick=nick, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    nick = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'nick'
    REQUIRED_FIELDS = []  # No extra fields required besides the username

    def __str__(self):
        return self.nick

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin