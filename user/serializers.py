
from rest_framework import serializers
from .models import *
from classes.models import *
from identity.models import *
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from datetime import timedelta

from django.contrib.auth import get_user_model
User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    profile_status = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'country', 'gender', 'profile_status']
    
    def get_profile_status(self, obj):
        if obj.request_delete == True:
            if obj.is_deleted == True:
                elapsed = timezone.now() - obj.deleted_date
                days_remaining = timedelta(days=30) - elapsed
                return f'Profile delete request approved on {obj.deleted_date}. {days_remaining} remaining'
            else:
                return 'Delete Profile Request Pending Approval'
        return True              

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'gender', 'country') 
        read_only_fields = ('username', 'email')  
        
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=50, write_only=True)
    new_password1 = serializers.CharField(label='New Password', max_length=50, write_only=True)
    new_password2 = serializers.CharField(label='New Confirm Password', max_length=50, write_only=True) 
    
    def validate_new_password1(self, value):
        validate_password(value)
        return value       


class UserPaidClassSerializer(serializers.ModelSerializer):
    online_class = serializers.SerializerMethodField()

    class Meta:
        model = ClassEnrollment
        fields = ['online_class', 'id','payment_date', 'amount_paid', 'enrollment_status']  # Include desired fields from ClassEnrollment

    def get_online_class(self, obj):
        status = 'Class Deactivated' if not obj.online_class.is_active else 'Active'
        class_data = {
            'id': obj.online_class.id,
            'title': obj.online_class.title,
            'description': obj.online_class.description,
            'start_time': obj.online_class.start_time,
            'end_time': obj.online_class.end_time,
            'price': obj.online_class.price,
            'slug': obj.online_class.slug,
            'status': status,
        }
        return class_data
    
     
class UserClassEnrollmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassEnrollment
        fields = ['enrollment_status']
        read_only_fields = ['user', 'online_class', 'paid', 'payment_date', 'amount_paid']

    def update(self, instance, validated_data):
        instance.enrollment_status = validated_data.get('enrollment_status', instance.enrollment_status)
        instance.save()
        return instance       


class DeleteProfileRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['request_delete']
        read_only_fields = ['request_delete']
    
    def update(self, instance, validated_data):
        if instance.request_delete == True:
            raise serializers.ValidationError("Delete Already Requested!")
    
        if instance.is_deleted == True:
            raise serializers.ValidationError("Account will be deleted after within 30 days")

        instance.request_delete = True
        instance.save()
        return instance  