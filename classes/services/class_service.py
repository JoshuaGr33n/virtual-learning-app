from repositories.repository import Repository
from classes.models import *
from ..serializers import  *
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.core.exceptions import PermissionDenied


class ClassService:
    
    def __init__(self):
        self.model = OnlineClass
        self.backgroundModel = ClassBackgroundImage
        self.repository = Repository(OnlineClass)
        self.backgroundRepository = Repository(ClassBackgroundImage)
        self.messagesRepository = Repository(ClassMessage)
     
    def get_all_classes(self):
        classes = self.repository.filter_objects(is_active=True)
        if classes.exists():
            serializer = ClassSerializer(classes, many=True)
            return serializer.data 
        else:
            return [] 
    
    def get_class(self, class_id):
        try:
            class_n = self.repository.get_object(id=class_id)
            serializer = ClassSerializer(class_n) 
            return serializer.data
        except class_n.DoesNotExist:
            raise Http404("Class not found")
    
    def get_background(self, user):
        try:
            background = self.backgroundRepository.get_object(user=user)
            serializer = ClassBackgroundImageSerializer(background) 
            return serializer.data
        except background.DoesNotExist:
            raise Http404("Background not found")    
        
    
    def add_or_update_background(self, user, data):
        try:
            # Attempt to get the existing background image for the user
            background_image = self.backgroundRepository.get_object(user=user)
            updated_image = self.backgroundRepository.update2(background_image, **data)
        except self.backgroundModel.DoesNotExist:
            # If no background image exists for this user, create a new one
            data['user'] = user
            data['name'] = data.get('name', f'Background_{user.username}')
            return self.backgroundRepository.create2(**data)
        return updated_image    
    

    def get_class_messages(self, class_id):
        try:
            self.repository.get_object(id=class_id)
        except Http404:
            raise Http404(f"Class with id {class_id} does not exist.")
        messages = self.messagesRepository.filters(class_id=class_id)
        if messages.exists():
            serializer = GetClassMessagesSerializer(messages, many=True)
            return serializer.data 
        else:
            return []
    
    
    def get_single_message(self, user, class_id, message_id):   
        try:
            self.repository.get_object(id=class_id)
        except Http404:
            raise Http404(f"Class with id {class_id} does not exist.")

        try:
            message = self.messagesRepository.get_object(id=message_id, class_id=class_id)
        except Http404:
            raise Http404("Message not found or does not belong to the specified class.")

        if not message.sender == user:
            raise PermissionDenied("You don't have access to this message.")
        serializer = GetClassMessagesSerializer(message)
        return serializer.data     
    
    
    def edit_message(self, class_id, message_id, data):
        message = self.messagesRepository.get_object(id=message_id, class_id=class_id)
        data['edited'] = True 
        updated_message = self.messagesRepository.update2(message, **data)
        return updated_message
    
    def delete_message(self, class_id, message_id):
        message = self.messagesRepository.get_object(id=message_id, class_id=class_id)
        message.delete()
        
    def clear_all_class_messages(self, class_id):
        try:
            self.repository.get_object(id=class_id)
        except Http404:
            raise Http404(f"Class with id {class_id} does not exist.")
        messages = self.messagesRepository.filters(class_id=class_id)
        if messages.exists():
            messages.delete()
        else:
            return []    