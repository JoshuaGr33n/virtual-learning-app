from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *



router = DefaultRouter()

urlpatterns = [
   path('register-user/', UserRegistrationAPIView.as_view(), name='user_registration'),
   path('verify-account/', verify_account, name='verify-account'),
   path('regenerate-otp/', regenerate_otp, name='regenerate_otp'),
   path('user-login/', UserLoginAPIView.as_view(), name='user_login'),
   
   path('forgot-password/', ForgetPasswordAPIView.as_view(), name='api-forget-password'),
   path('reset-password/', ResetPasswordAPIView.as_view(), name='api-reset-password'),
   ]

