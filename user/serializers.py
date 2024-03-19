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
        fields = ['online_class', 'id','payment_date', 'amount_paid', 'enrollment_status']

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
    
    

class FriendRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['id', 'sender', 'receiver']
        read_only_fields = ['sender', 'id']  # 'sender' is determined by the logged-in user
    
    def validate_receiver(self, value):
        sender = self.context['request'].user
        if sender == value:
            raise serializers.ValidationError("You cannot send a friend request to yourself.")
       
        sent = FriendRequest.objects.filter(sender=sender, receiver=value).first()
        received = FriendRequest.objects.filter(sender=value, receiver=sender).first()
        
        if sent:
            if sent.status == 'declined':
                # Update the status of the previously declined request instead of creating a new one
                sent.status = 'sent'
                sent.save(update_fields=['status'])
                raise serializers.ValidationError("The friend request has been re-sent.")
            elif sent.status == 'accepted':
                raise serializers.ValidationError("You are already friends with this user.") 
            else:
                raise serializers.ValidationError("A friend request has already been sent to this user.")
        
        if received:
            if received.status == 'declined':
                # Update the status of the previously declined request instead of creating a new one
                received.status = 'sent'
                received.receiver = value
                received.sender = self.context['request'].user
                received.save(update_fields=['status', 'receiver','sender'])
                raise serializers.ValidationError("The friend request has been re-sent.")
            elif received.status == 'accepted':
                raise serializers.ValidationError("You are already friends with this user.") 
            else:
                raise serializers.ValidationError("You already received a friend request from this user")
        
        return value
    
    def create(self, validated_data):
        return super().create(validated_data)
    
    
    
class FriendRequestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['status']


class UserFriendSerializer(serializers.ModelSerializer):
    friend_username = serializers.SerializerMethodField()
    class Meta:
        model = FriendRequest
        fields = ['friend_username', 'status']
        
    def get_friend_username(self, obj):
        request_user = self.context.get('request').user if 'request' in self.context else None

        if request_user:
            if obj.sender == request_user:
                return obj.receiver.username
            else:
                return obj.sender.username
        else:
            return None


class UserFriendRequestsSerializer(serializers.ModelSerializer):
    receiver = serializers.SerializerMethodField()
    sender = serializers.SerializerMethodField()
    class Meta:
        model = FriendRequest
        fields = ['id', 'sender', 'receiver', 'status']
        
    def get_sender(self, obj):
        return obj.sender.username
    
    def get_receiver(self, obj):
        return obj.receiver.username    
            
