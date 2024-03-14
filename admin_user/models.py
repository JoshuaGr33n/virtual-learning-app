from django.db import models
from identity.models import *
from django.contrib.auth.tokens import default_token_generator

class Admin_User(User):
    USER_TYPE = (
        ('Admin', 'Admin'),
        ('Sub-Admin', 'Sub-Admin'),
    )
    user_type = models.CharField(choices=USER_TYPE, blank=True, null=True, max_length=50)
    login_url = models.URLField(blank=True, null=True)
    token = models.CharField(max_length=400, default='No-Token')
    
    def save(self, *args, **kwargs):
        # Check if the instance is new
        if not self.pk:
            # Generate a token for the new instance
            token = default_token_generator.make_token(self)  # Use self here
            self.token = token
            self.login_url = f'http://127.0.0.1:8000/api/admin-user/login/{token}/'
        # Always set is_admin to True
        self.is_admin = True
        # Call the superclass's save method
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return self.username


class Admin_OTP(models.Model):
    admin = models.OneToOneField(Admin_User, on_delete=models.CASCADE, related_name='admin_otp')
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
        self.otp_expiry = timezone.now() + datetime.timedelta(minutes=5) 
        self.save()

    def verify_otp(self, otp, type):    
        if timezone.now() <= self.otp_expiry and self.otp == otp and self.otp_type == type:
            self.otp = None 
            self.otp_type = None
            self.save()
            return True
        return False