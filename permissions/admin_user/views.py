from django.shortcuts import render
from rest_framework.response import Response
from django.contrib.auth import update_session_auth_hash
from rest_framework import status, generics
from rest_framework.views import APIView
from .models import *
from .serializers import *
from user.forms import *
from templatetags.custom_template_tags import *
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

from permissions.permissions import IsAdmin

class AdminUserCreationAPI(generics.ListCreateAPIView):
    queryset = Admin_User.objects.all()
    serializer_class = AdminUserCreationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = serializer.save()
        login_url = user.login_url
        admin_login_url_mail(user, login_url, subject = 'Your Login URL', status='')
        return Response({
            'user': serializer.data,
            'login_url': login_url,
            'message':'Admin Created. Check email for login url'
        }, status=status.HTTP_201_CREATED)

class AdminLogin(APIView):
    serializer_class = AdminLoginSerializer
    def post(self, request, token=None, *args, **kwargs):
        serializer = AdminLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            admin_user = Admin_User.objects.get(username=username)
            
            if admin_user.token == token:
                otp = admin_user.admin_otp.otp
                
                otp_mail(admin_user, otp, subject = 'OTP for Login Your Account!',  status="")
                
                return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)
                
            else:
                return Response({'message': 'Invalid Token!'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
class AdminLoginOTPVerification(APIView):
    def post(self, request, *args, **kwargs):
        serializer = AdminOTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Account successfully verified.',
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            })
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)       


class EmailUser:
    def __init__(self, email):
        self.email = email
class AdminForgetPasswordAPIView(APIView):
    serializer_class = AdminForgetPasswordSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={})
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.context['otp'] 
            user = EmailUser(email=email)
            otp_mail(user, otp, subject = 'OTP for Password Reset!',  status="")
            return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminResetPasswordAPIView(APIView):
    serializer_class = AdminResetPasswordSerializer
    def post(self, request, *args, **kwargs):
        serializer = AdminResetPasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.context.get('user')
            new_password = serializer.validated_data['password1']
            user.set_password(new_password)
            user.save()
            return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = AdminChangePasswordSerializer
    def post(self, request, *args, **kwargs):
        serializer = AdminChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            form = ChangePasswordForm(request.user, data=serializer.validated_data)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                return Response({'detail': 'Password changed successfully!'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': form.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)    