from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *



router = DefaultRouter()

urlpatterns = [
   path('all-classes/', AllClassesView.as_view(), name='all-classes'),
   path('class/<uuid:class_id>/', GetClassView.as_view(), name='get-class'),
   
   path('background/', ClassBackgroundImageView.as_view(), name='class-background'),
   
   path('class/<uuid:class_id>/messages/', ClassMessagesView.as_view(), name='get-class-messages'),
   path('class/<uuid:class_id>/message/<uuid:message_id>/', ClassSingleMessageView.as_view(), name='get-message'),
   path('class/<uuid:class_id>/messages/delete/', AdminClearAllClassMessagesView.as_view(), name='delete-class-messages'),

]