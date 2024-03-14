from ..repositories.repository import Repository
from ..models import App, Subscription, Plan
from ..serializers import  SubscriptionSerializer, SubscriptionUpdateSerializer, PlanSerializer
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.http import Http404

class SubscriptionService:
    
    def __init__(self):
        self.repository = Repository(Subscription)

    def get_subscription(self, user, app_id):
       
        app = self.repository.get_object_or_none(App, pk=app_id, user=user)
        if not app:
            return Response({'message': 'App not found or does not belong to the user'}, status=status.HTTP_404_NOT_FOUND)

        subscription = self.repository.get_object_or_none(Subscription, app=app)
        if not subscription:
            return Response({'message': 'Subscription not found'}, status=status.HTTP_404_NOT_FOUND)
        try:
            serializer = SubscriptionSerializer(subscription)
            return Response(serializer.data)
        except self.repository.model.DoesNotExist:
            return Response({'message': 'Subscription not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def get_user_subscriptions(self, user):
        subscriptions = self.repository.filter_objects(app__user=user)
        if subscriptions.exists():
            serializer = SubscriptionSerializer(subscriptions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'No subscriptions'}, status=status.HTTP_404_NOT_FOUND)
     
    
    def update_subscription(self, user, subscription_id, update_data):
        try:
            subscription = self.repository.get_object(pk=subscription_id)
        except Subscription.DoesNotExist:
            raise Http404('Subscription not found.')

        if subscription.app.user != user:
            raise PermissionDenied('Permission denied. This subscription does not belong to this user.')

        serializer = SubscriptionUpdateSerializer(subscription, data=update_data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            response_data = {
                **serializer.data,  
                'message': 'Subscription updated successfully.'
                }
            return response_data
    
class PlanService:
    
    def __init__(self):
        self.repository = Repository(Plan)

    def get_plans(self):
        plans = self.repository.filter_objects()
        if plans.exists():
            serializer = PlanSerializer(plans, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'No Plans Predefined'}, status=status.HTTP_404_NOT_FOUND)    
        
    
    
    

