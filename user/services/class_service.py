from repositories.repository import Repository
from classes.models import *
from ..serializers import  *
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404

class ClassService:
    
    def __init__(self):
        self.online_class_repository = Repository(OnlineClass)  # Ensure this is defined
        self.repository = Repository(ClassEnrollment)
     
    def paid_classes(self, user):
        enrollments = self.repository.filter_objects(user=user, paid=True)
        if enrollments.exists():
            serializer = UserPaidClassSerializer(enrollments, many=True)
            return serializer.data
        else:
            return []

    
    def get_paid_class(self, user, class_id):
        try:
            paid_class = self.repository.get_object_or_fail(user=user, paid=True, online_class=class_id)
            serializer = UserPaidClassSerializer(paid_class) 
            return serializer.data
        except paid_class.DoesNotExist:
            raise Http404("Class not found")
    
   
    def user_join_class(self, user, class_id):
        online_class = self.online_class_repository.get_object_or_fail(id=class_id)
        if not online_class:
            raise Http404("Class not found")
        
        if not online_class.is_active:
            raise ValueError("This class is currently deactivated.")

        # Check if a paid, active enrollment exists
        enrollment = self.repository.filter_objects(user=user, online_class=online_class, paid=True, enrollment_status='active').first()
        
        if enrollment:
            return True
        elif self.repository.filter_objects(user=user, online_class=online_class, paid=True, enrollment_status='cancelled').exists():
            raise ValueError("Your enrollment has been cancelled.")
        else:
            return False


    def update_enrollment_status(self, user, enrollment_id, status):
        enrollment = self.repository.get_object_or_fail(id=enrollment_id)
        if not enrollment:
            return False
        
        if enrollment.user == user:
            serializer = UserClassEnrollmentUpdateSerializer(enrollment, data={'enrollment_status': status})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return True
        else:
            raise PermissionError("You not authorized to update this enrollment")      