from repositories.repository import Repository
from classes.models import *
from identity.models import User
from ..serializers import  *
from classes.serializers import *
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
        self.user_repository = Repository(User)
        

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

    def get_all_enrollments(self):
        enrollments = self.enrollment_repository.filter_objects()
        if enrollments.exists():
            serializer = ListClassEnrollmentsSerializer(enrollments, many=True)
            return serializer.data 
        else:
            return []
    
    def get_user_enrollments(self, pk):
        try:
            class_n = self.user_repository.get_object(pk=pk)
        except self.model.DoesNotExist:
            raise Http404('User not found.')
        
        enrollments = self.enrollment_repository.filter_objects(user=pk)
        if enrollments.exists():
            serializer = ListClassEnrollmentsSerializer(enrollments, many=True)
            return serializer.data 
        else:
            return []         
    
class AdminApproveClassPaymentService:
    def __init__(self):
        self.online_class_repository = Repository(OnlineClass)
        self.enrollment_repository = Repository(ClassEnrollment)
        self.user_repository = Repository(User)

    def approve_payment(self, user, class_id):
        online_class = self.online_class_repository.get_object_or_fail(id=class_id)
        user = self.user_repository.get_object_or_fail(id=user)
        if not online_class:
            raise Http404("Class not found")
        
        if not user:
            raise Http404("User not found")
        
        if online_class.is_active == False:
            raise Http404("Class deactivated. Activate class first")
        
       
        existing_enrollment = self.enrollment_repository.filter_objects(
            user=user, 
            online_class_id=class_id, 
            paid=True
        )
        
        if existing_enrollment.exists():
            # If user has already paid for the class
            return {"message": "This user have already paid for this class."}, status.HTTP_409_CONFLICT

        try:
            # If the charge is successful, record the enrollment and payment
            self.enrollment_repository.create({
                'user': user,
                'online_class': online_class,
                'paid': True,
                'payment_date': timezone.now(),
                'amount_paid': online_class.price
            })
            return {"message": "Approval successful"}, status.HTTP_200_OK
        except Exception as e:
            print(f"Unexpected error: {e}")
            return {"message": "An unexpected error occurred."}, status.HTTP_400_BAD_REQUEST
    