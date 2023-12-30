from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.contrib.auth.forms import UserCreationForm, AbstractUser # type: ignore




class User(AbstractUser):
    pass