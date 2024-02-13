from enum import unique
from tabnanny import verbose
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from traitlets import default

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from datetime import datetime

user_role_choice = (
    ("Admin", "Admin"),
    ("Contractor", "Contractor")
)

gender_choice = (
    ("Male", "Male"),
    ("Female", "Female")
)

labour_category = (
    ("General Workers", "General Workers"),
    ("Skilled Workers", "Skilled Workers")
)


# Create your models here.

class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, first_name, last_name, phone=None, password=None):
        if not email:
            raise ValueError("User must have an email address")
        if not username:
            raise ValueError("User must have a username")
        if not first_name:
            raise ValueError("User must have a first name")
        if not last_name:
            raise ValueError("User must have a last name")

        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
            user_role = "Contractor"
        )

        if phone != None:
            user.phone = phone

        user.set_password(password)
        user.save(using=self.db)
        return user

    
    def create_superuser(self, email, username, first_name, last_name, password, phone=None):
        user = self.create_user(
            email = email,
            username = username,
            password = password,
            first_name = first_name,
            last_name = last_name,
        )
        user.user_role = "Admin"
        user.is_verified = True
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self.db)
        if phone != None:
            user.phone = phone
        return user



class Account(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(verbose_name="email", max_length=254, unique=True)
    username = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    user_role = models.CharField(max_length=50, choices=user_role_choice)
    phone = models.CharField(max_length=20)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(verbose_name="date joined", auto_now_add=True)
    last_login = models.DateTimeField(verbose_name="last login", auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    objects = MyAccountManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perm(self, app_label):
        return True



class Skill(models.Model):
    category = models.CharField(max_length=50, choices=labour_category, default="General Workers")
    skill = models.CharField(max_length=100, primary_key=True)
    count = models.IntegerField(default=0)
    cost_per_hour_normal_days_less_than_four = models.IntegerField(default=0)
    cost_per_hour_normal_days_less_than_eight = models.IntegerField(default=0)
    cost_per_hour_normal_days_less_than_twelve = models.IntegerField(default=0)
    cost_per_hour_public_holiday_less_than_four = models.IntegerField(default=0)
    cost_per_hour_public_holiday_less_than_eight = models.IntegerField(default=0)
    cost_per_hour_public_holiday_less_than_twelve = models.IntegerField(default=0)

    def __str__(self):
        return self.skill


class Labour(models.Model):
    labour_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=500)
    last_name = models.CharField(max_length=500)
    email = models.EmailField(max_length=500)
    gender = models.CharField(max_length=50, choices=gender_choice)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    phone = models.CharField(max_length=10)
    passport_no = models.CharField(max_length=100)


class Booking(models.Model):
    booking_id = models.AutoField(primary_key=True)
    contractor_name = models.CharField(max_length=500)
    contractor_email = models.EmailField()
    labour_skill = models.CharField(max_length=500)
    labour_count = models.IntegerField()
    labour_gender = models.CharField(max_length=10, default="Male")
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=1000)
    status = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=100, default="Pending") # Pending/Complete


class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    booking_id = models.ForeignKey(Booking, on_delete=models.PROTECT) # order_id
    transaction_id = models.IntegerField(default=0)
    payment_date_time = models.DateTimeField(default=datetime.now())
    payment_status = models.CharField(max_length=10, default="-1")
    merchant_id = models.CharField(max_length=100, default="null")
    country = models.CharField(max_length=20, default="null")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    


class LaboursAllocated(models.Model):
    allocation_id = models.AutoField(primary_key=True)
    booking_id = models.ForeignKey(Booking, on_delete=models.CASCADE)
    labour_id = models.ForeignKey(Labour, on_delete=models.PROTECT)


class PublicHoliday(models.Model):
    event = models.CharField(max_length=1000)
    date = models.DateField()


class Notification(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(Account, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    date_and_time = models.DateTimeField()
    is_read = models.BooleanField(default=False)

 
# Token generation while user is registered
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)



