from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *



router = DefaultRouter()

urlpatterns = [
    path('create-admin/', AdminUserCreationAPI.as_view(), name='create-admin'),
    path('login/<token>/', AdminLogin.as_view(), name='api-login-token'),
    path('login-verification/', AdminLoginOTPVerification.as_view(), name='admin-login-otp-verification'),
    path('forget-password/', AdminForgetPasswordAPIView.as_view(), name='api-admin-forget-password'),
    path('reset-password/', AdminResetPasswordAPIView.as_view(), name='api-admin-reset-password'), 
    path('change-password/', AdminChangePasswordAPIView.as_view(), name='admin-change-password-api'),
]
