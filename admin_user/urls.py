from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *



router = DefaultRouter()

urlpatterns = [
    path('create-admin/', AdminUserCreationAPI.as_view(), name='create-admin'),
    path('login/<token>/', AdminLogin.as_view(), name='api-login-token'),
    path('login-verification/', AdminLoginOTPVerification.as_view(), name='admin-login-otp-verification'),
    path('admin-profile/', AdminProfileView.as_view(), name='admin-profile'),
    path('forget-password/', AdminForgetPasswordAPIView.as_view(), name='api-admin-forget-password'),
    path('reset-password/', AdminResetPasswordAPIView.as_view(), name='api-admin-reset-password'), 
    path('change-password/', AdminChangePasswordAPIView.as_view(), name='admin-change-password-api'),
    path('create-class/', AdminCreateNewClassView.as_view(), name='admin-create-class'),
    
    path('<uuid:pk>/update-class/', AdminUpdateClassView.as_view(), name='class-update'),
   #  path('classes/<slug:slug>/delete/', OnlineClassDeleteView.as_view(), name='class-delete'),
   
   path('enrollments/<uuid:enrollment_id>/activate/', AdminEnrollmentStatusUpdateView.as_view(), {'status': 'Active'}, name='activate-enrollment'),
   path('enrollments/<uuid:enrollment_id>/cancel/', AdminEnrollmentStatusUpdateView.as_view(), {'status': 'Cancelled'}, name='cancel-enrollment'),
   
    path('classes/<uuid:class_id>/activate/', ActivateClassView.as_view(), name='activate-class'),
    path('classes/<uuid:class_id>/deactivate/', DeactivateClassView.as_view(), name='deactivate-class'),
     path('enrollments/<uuid:enrollment_id>/activate/', AdminEnrollmentStatusUpdateView.as_view(), {'status': 'Active'}, name='activate-enrollment'),
    
    path('user/<int:pk>/deactivate/', AdminManageUserProfileView.as_view(), {'status': 'deactivate'}, name='deactivate-user'),
    path('user/<int:pk>/activate/', AdminManageUserProfileView.as_view(), {'status': 'activate'}, name='activate-user'),
    path('user/<int:pk>/', AdminManageUserProfileView.as_view(), name='user-profile'),
    path('users/', AdminGetAllUsers.as_view(), name='all-users'),
    
     path('approve-profile-delete-request/<int:pk>', AdminApproveUserProfileDeleteRequestAPIView.as_view(), name='approve-profile-delete-request'),
     path('cancel-delete-profile-request/<int:pk>', AdminCancelUserProfileDeleteRequestAPIView.as_view(), name='cancel-delete-profile-request'),
   
]
  