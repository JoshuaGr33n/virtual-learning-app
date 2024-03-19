from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework import mixins
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from templatetags.custom_template_tags import *

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.decorators import api_view, permission_classes
User = get_user_model()
from permissions.permissions import *

class UserRegistrationAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            otp = user.user_otp.otp

            otp_mail(user, otp, subject = 'OTP for Account Verification!', status='')

            return Response({
                'user': user.username,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'Please verify your account using the OTP sent to your email.'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_account(request):
    user = request.user
    otp = request.data.get('otp')
    if otp is None:
            return Response({"error": "OTP not provided."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        otp_int = int(otp)
    except ValueError:
        return Response({"error": "OTP must be a valid integer."}, status=status.HTTP_400_BAD_REQUEST)

    if user.user_otp.verify_otp(int(otp), type="Login"):
        return Response({'message': 'Account successfully verified.'})
    else:
        return Response({'error': 'Invalid or expired OTP.'}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['POST'])
def regenerate_otp(request):
    serializer = RegenerateOTPSerializer(data=request.data)
    
    if serializer.is_valid():
        validated_data = serializer.save()
        user = validated_data['user']
        new_otp = validated_data['new_otp']
        
        refresh = RefreshToken.for_user(user)  
            
        otp_mail(user, new_otp, subject = 'OTP for Account Verification!', status="new")
        
        return Response({
            'message': 'OTP regenerated and sent successfully.',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
          
class UserLoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                "message":'Login Successful',
                'access': str(refresh.access_token),
                'refresh': str(refresh),  
            })

        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED) 


class EmailUser:
    def __init__(self, email):
        self.email = email
class ForgetPasswordAPIView(APIView):
    serializer_class = ForgetPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={})
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.context['otp'] 
            user = EmailUser(email=email)
            otp_mail(user, otp, subject = 'OTP for Password Reset!',  status="")
            return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordAPIView(APIView):
    serializer_class = ResetPasswordSerializer
    def post(self, request, *args, **kwargs):
        serializer = ResetPasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.context.get('user')
            new_password = serializer.validated_data['password1']
            user.set_password(new_password)
            user.save()
            return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def post(self, request):
        print(request.data)
        try:
            # Assuming the refresh token is sent in the body of the request
            refresh_token = request.data.get('refresh_token')
            if refresh_token is None:
                return Response({"error": "Refresh token not provided."}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": f"Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
        except TokenError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
     
 
 


