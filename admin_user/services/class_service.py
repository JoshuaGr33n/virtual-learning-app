from repositories.repository import Repository
from classes.models import *
from ..serializers import  *
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError
from django.http import Http404
from django.core.exceptions import PermissionDenied

class ClassService:
    
    def __init__(self):
        self.model = OnlineClass
        self.repository = Repository(self.model)
        self.enrollment_repository = Repository(ClassEnrollment)
        

    def create_class(self, data, user):
        serializer = AdminCreateClassSerializer(data=data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            validated_data['created_by'] = user
            try:
                class_n = self.repository.create(validated_data)
                return Response(AdminCreateClassSerializer(class_n).data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                 return Response({'error': f'{validated_data["title"]} already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
     
    
    def update_class(self, user, pk, update_data):
        try:
            class_n = self.repository.get_object(pk=pk)
        except self.model.DoesNotExist:
            raise Http404('Class not found.')

        serializer = AdminUpdateClassSerializer(class_n, data=update_data, partial=True)
        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()  
                response_data = {
                **serializer.data,  
                'message': 'Class updated successfully.'
                }
                return response_data
            except IntegrityError:
                return {'error': f"{update_data.get('title', class_n.title)} already exists.", 'status': status.HTTP_400_BAD_REQUEST}
        else:
            return {'error': serializer.errors, 'status': status.HTTP_400_BAD_REQUEST}
    
    
    def update_enrollment_status(self, enrollment_id, status):
        enrollment = self.enrollment_repository.get_object_or_fail(id=enrollment_id)
        if enrollment:
            serializer = ClassEnrollmentUpdateSerializer(enrollment, data={'enrollment_status': status})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return True
        return False
    

    def activate_class(self, class_id):
        online_class = self.repository.get_object_or_fail(id=class_id)
        if not online_class:
            raise Http404("Class not found")
        serializer = OnlineClassActivationSerializer(instance=online_class, data={'is_active': True})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return "Class activated successfully."
        return "Failed to activate class."

    def deactivate_class(self, class_id):
        online_class = self.repository.get_object_or_fail(id=class_id)
        if not online_class:
            raise Http404("Class not found")
        serializer = OnlineClassActivationSerializer(instance=online_class, data={'is_active': False})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return "Class deactivated successfully."
        return "Failed to deactivate class."
    
    