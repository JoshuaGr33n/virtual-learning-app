from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
import datetime

COUNTRY_CHOICES = (
    ('india', 'India'),
    ('bangladesh', 'Bangladesh'),
    ('malaysia', 'Malaysia'),
    ('singapore', 'Singapore'),
)
class User(AbstractUser):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=10, choices=(('male', 'Male'), ('female', 'Female')))
    country = models.CharField(max_length=100, choices=COUNTRY_CHOICES)
    email = models.EmailField(unique=True)
    is_admin = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    request_delete = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    deleted_date = models.DateTimeField(null=True, blank=True)


class User_OTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_otp')
    otp = models.IntegerField(null=True, blank=True)
    otp_expiry = models.DateTimeField(null=True, blank=True)
    OTP_TYPE = (
        ('Password', 'Password'),
        ('Login', 'Login'),
    )
    otp_type = models.CharField(choices=OTP_TYPE, blank=True, null=True, max_length=50, default='Login')

    def set_otp(self, otp, type):
        self.otp = otp
        self.otp_type = type
        self.otp_expiry = timezone.now() + datetime.timedelta(minutes=5)  # OTP expires in 5 minutes
        self.save()

    def verify_otp(self, otp, type):
        if timezone.now() <= self.otp_expiry and self.otp == otp and self.otp_type == type:
            self.otp = None
            if type == "Login":
                self.user.is_verified = True 
            self.otp_type = None
            self.user.save() 
            self.save()
            return True
        return False    