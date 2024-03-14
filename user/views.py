from django.shortcuts import render, get_object_or_404
from .models import *
from .serializers import *
from rest_framework import status
from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import update_session_auth_hash
from .forms import ChangePasswordForm
from templatetags.custom_template_tags import *

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.exceptions import TokenError

from permissions.permissions import *

from .services.online_class_payment import OnlineClassPaymentService
from .services.class_service import *


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]
    def get(self, request):
        user_profile = get_object_or_404(User, username=request.user.username)
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True) 
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    


class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated,  IsVerifiedUser]
    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
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
        
        
class ClassPaymentView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]
    def post(self, request, class_id):
        token = request.data.get('stripeToken')
        service = OnlineClassPaymentService()

        result, http_status = service.process_payment(request.user, class_id, token)
        return Response(result, status=http_status)
 
 
class UserPaidClassesListView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]
    def get(self, request):
        class_service = ClassService()
        classes_data = class_service.paid_classes(request.user)
        if classes_data:
            return Response(classes_data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'No classes created'}, status=status.HTTP_404_NOT_FOUND)


class UserPaidClassView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]
    def get(self, request, class_id, *args, **kwargs):
        class_service = ClassService()
        try:
            response_data = class_service.get_paid_class(request.user, class_id)
            return Response(response_data) 
        except Http404 as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)        
 
 
class UserJoinClassView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def get(self, request, class_id):
        class_service = ClassService()

        try:
            if class_service.user_join_class(request.user, class_id):
                return Response({'message': 'Welcome to the class!'}, status=status.HTTP_200_OK)
        except Http404:
            return Response({'error': 'Class not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)

        return Response({'error': 'You must pay for the class before joining.'}, status=status.HTTP_403_FORBIDDEN)
 
 
class UserEnrollmentStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def post(self, request, enrollment_id, *args, **kwargs):
        status_to_update = kwargs.get('status')
        class_service = ClassService()
        try:
            if class_service.update_enrollment_status(request.user, enrollment_id, status_to_update):
                return Response({'message': f'Enrollment {status_to_update} successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid request or enrollment not found.'}, status=status.HTTP_404_NOT_FOUND)
        except PermissionError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Http404:
            return Response({'error': 'Enrollment not found'}, status=status.HTTP_404_NOT_FOUND)    

 
class UserDeleteProfileRequestAPIView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def delete(self, request):
        user = request.user
        serializer = DeleteProfileRequestSerializer(user, data={}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Success! Account will be deleted 30 days after admin approval.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
 
 
def test_stripe(request):
    return render(request, 'stripe.html', {})
        
        