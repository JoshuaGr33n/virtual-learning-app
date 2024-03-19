from django.shortcuts import render, get_object_or_404
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
from .services.class_service import *
from .services.admin_service import *
from permissions.permissions import *

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
       
       
class AdminProfileView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    def get(self, request):
        user_profile = get_object_or_404(User, username=request.user.username)
        serializer = AdminProfileSerializer(user_profile)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = AdminProfileSerializer(request.user, data=request.data, partial=True) 
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
        
class AdminCreateNewClassView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    def post(self, request):
        class_service = ClassService()
        return class_service.create_class(request.data, request.user)

class AdminUpdateClassView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    def put(self, request, pk, *args, **kwargs):
        class_service = ClassService()
        try:
            updated_data = class_service.update_class(request.user, pk, request.data)
            return Response(updated_data, status=status.HTTP_200_OK)
        except Http404 as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
                

class AdminEnrollmentStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, enrollment_id, *args, **kwargs):
        status_to_update = kwargs.get('status')
        class_service = ClassService()

        if class_service.update_enrollment_status(enrollment_id, status_to_update):
            return Response({'message': f'Enrollment {status_to_update} successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid request or enrollment not found.'}, status=status.HTTP_404_NOT_FOUND)


class ActivateClassView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, class_id):
        class_service = ClassService()
        message = class_service.activate_class(class_id)
        return Response({'message': message})


class DeactivateClassView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, class_id):
        class_service = ClassService()
        message = class_service.deactivate_class(class_id)
        return Response({'message': message})


class AdminManageUserProfileView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    def get(self, request, pk):
        user_profile = get_object_or_404(User, pk=pk)
        if user_profile == request.user:
            return Response({'message': 'Not Allowed'}, status=status.HTTP_403_FORBIDDEN)
        serializer = AdminManageUserProfileSerializer(user_profile)
        return Response(serializer.data)
    
    def put(self, request, pk, *args, **kwargs):
            status_to_update = kwargs.get('status')
            user_profile = get_object_or_404(User, pk=pk)
            if user_profile == request.user:
                return Response({'message': 'Not Allowed'}, status=status.HTTP_403_FORBIDDEN)
            
            if status_to_update == 'activate':
                status_v = True
            else:
                status_v = False
                    
            serializer = AdminManageUserSerializer(user_profile, data={'is_active': status_v})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                message = {'message': f'User {status_to_update}d successfully.'}
                response_data = {**message, **serializer.data}
                return Response(response_data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
            
class AdminGetAllUsers(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    def get(self, request, *args, **kwargs):
        admin_service = AdminService()
        
        filters = {}
        if 'verified' in request.query_params:
            filters['is_verified'] = request.query_params['verified'].lower() in ['true', '1', 't', 'y', 'yes']
        
        if 'active' in request.query_params:
            filters['is_active'] = request.query_params['active'].lower() in ['true', '1', 't', 'y', 'yes']
        
        if 'request_delete' in request.query_params:
            filters['request_delete'] = request.query_params['request_delete'].lower() in ['true', '1', 't', 'y', 'yes']    
        
        if 'deleted' in request.query_params:
            filters['request_delete'] = request.query_params['deleted'].lower() in ['true', '1', 't', 'y', 'yes']        
        
        users_data = admin_service.get_all_users(filters)
        if users_data:
            
            return Response(users_data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'No users yet'}, status=status.HTTP_404_NOT_FOUND)    
        

class AdminApproveUserProfileDeleteRequestAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)

        serializer = AdminApproveUserProfileDeleteRequestSerializer(user, data={}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Delete Request Approved. Account will be taken down in 30 days'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminCancelUserProfileDeleteRequestAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    def post(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        serializer = AdminCancelDeleteProfileRequestSerializer(user, data={}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Delete request cancelled'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminApproveClassPaymentView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    def post(self, request, class_id):
        serializer = AdminApproveClassPaymentSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            service = AdminApproveClassPaymentService()
            try:
                result, http_status = service.approve_payment(user, class_id)
                return Response(result, status=http_status)
            except Http404 as e:
                return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminListClassEnrollmentsView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    def get(self, request, *args, **kwargs):
        class_service = ClassService()
        enrollments = class_service.get_all_enrollments()
        if enrollments:
            return Response(enrollments, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'No enrollments created'}, status=status.HTTP_404_NOT_FOUND)
  

class AdminListUserEnrollmentsView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    def get(self, request, pk, *args, **kwargs):
        class_service = ClassService()
        try:
            enrollments = class_service.get_user_enrollments(pk)
            if enrollments:
                return Response(enrollments, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'No enrollments created'}, status=status.HTTP_404_NOT_FOUND)
            
        except Http404 as e:
                return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)