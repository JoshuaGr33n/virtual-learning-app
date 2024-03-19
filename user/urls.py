from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *



router = DefaultRouter()

urlpatterns = [
   path('user-profile/', UserProfileView.as_view(), name='user-profile'),
   path('user-change-password/', ChangePasswordAPIView.as_view(), name='user-change-password'),
   
   path('classes/<uuid:class_id>/pay/', ClassPaymentView.as_view(), name='class-pay'),
   path('paid-classes/', UserPaidClassesListView.as_view(), name='paid-classes-list'),
   path('paid-class/<uuid:class_id>/', UserPaidClassView.as_view(), name='paid-class'),
   path('classes/<uuid:class_id>/join/', UserJoinClassView.as_view(), name='user-join-class'),
   path('enrollment/<uuid:enrollment_id>/cancel/', UserEnrollmentStatusUpdateView.as_view(), {'status': 'Cancelled'}, name='cancel-enrollment'),
   path('enrollments/', UserListEnrollmentsView.as_view(), name='enrollments'),
   
   path('delete-profile-request/', UserDeleteProfileRequestAPIView.as_view(), name='delete-profile-request'),
   
   path('send-friend-request/', SendFriendRequestView.as_view(), name='send-friend-request'),
   path('update-friend-request/<int:pk>/', UpdateFriendRequestView.as_view(), name='update-friend-request'),
   path('user-friend-list/', UserListFriendsView.as_view(), name='user-friend-list'),
   path('user-friend-requests/', UserFriendRequestsView.as_view(), name='user-friend-requests'),


   path('stripe', test_stripe, name="stripe"),
]

