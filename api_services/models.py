from enum import unique
from tabnanny import verbose
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from traitlets import default

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

# Create your models here.

class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, first_name, last_name, user_role, phone, password=None):
        if not email:
            raise ValueError("User must have an email address")
        if not username:
            raise ValueError("User must have a username")
        if not first_name:
            raise ValueError("User must have a first name")
        if not last_name:
            raise ValueError("User must have a last name")
        if not user_role:
            raise ValueError("User must have a role defined")
        if not phone:
            raise ValueError("User must have a phone number")

        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
            phone = phone,
            user_role = user_role
        )

        user.set_password(password)
        user.save(using=self.db)
        return user

    
    def create_superuser(self, email, username, first_name, last_name, user_role, phone, password):
        user = self.create_user(
            email = email,
            username = username,
            password = password,
            phone = phone,
            first_name = first_name,
            last_name = last_name,
            user_role = user_role
        )
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self.db)
        return user



class Account(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name="email", max_length=254, unique=True)
    username = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    user_role = models.CharField(max_length=100)
    phone = models.CharField(max_length=10)
    skills = models.CharField(max_length=5000)
    date_joined = models.DateTimeField(verbose_name="date joined", auto_now_add=True)
    last_login = models.DateTimeField(verbose_name="last login", auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name", "user_role", "phone"]

    objects = MyAccountManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perm(self, app_label):
        return True



# Model for Labour
class Labour(models.Model):
    skill = models.CharField(max_length=100, primary_key=True)
    count = models.IntegerField()
    cost_per_hour = models.IntegerField()


class Booking(models.Model):
    booking_id = models.IntegerField(primary_key=True)
    contractor_name = models.CharField(max_length=500)
    contractor_email = models.EmailField()
    labour_skill = models.CharField(max_length=500)
    labour_count = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=1000)


class Payment(models.Model):
    payment_id = models.IntegerField(primary_key=True)
    booking_id = models.IntegerField()
    payment_date = models.DateField()
    amount = models.IntegerField()
    status = models.CharField(max_length=100)

 
# Token generation while user is registered
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)



