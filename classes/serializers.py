from rest_framework import serializers
from .models import *
from django.core.files.images import get_image_dimensions
from PIL import Image
import os


class ClassSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField() 

    class Meta:
        model = OnlineClass
        fields = ['id', 'title', 'description', 'start_time', 'end_time', 'price', 'slug', 'created_by_name', 'status'] 
        read_only_fields = ['id', 'created_by', 'slug']

    def get_created_by_name(self, obj):
        return f'{obj.created_by.first_name} {obj.created_by.last_name}' if obj.created_by else None
    
    def get_status(self, obj):
        return 'Class Deactivated' if not obj.is_active else 'Active'


class ClassBackgroundImageSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    class Meta:
        model = ClassBackgroundImage
        fields = ['id', 'name', 'image', 'username']
        read_only_fields = ['user', 'name'] 
    
    def validate_image(self, value):
        if value.size == 0:
            raise serializers.ValidationError("The submitted file is empty.")
        try:
            img = Image.open(value)
            img.verify()  # Verify that it is an image
        except (IOError, ValueError):
            raise serializers.ValidationError("The submitted file is not a valid image.")
        
        # Image file size must be less than 5MB
        max_upload_size = 1024 * 1024 * 5
        if value.size > max_upload_size:
            raise serializers.ValidationError("Image file size must be less than 5MB.")

        #  Image dimensions must not be too small
        min_width, min_height = 100, 100
        width, height = get_image_dimensions(value)
        if width < min_width or height < min_height:
            raise serializers.ValidationError(f"Image must be at least {min_width}x{min_height} pixels.")

        # Restrict file types (extensions)
        allowed_extensions = ['.jpg', '.jpeg', '.png']
        ext = os.path.splitext(value.name)[1]
        if ext.lower() not in allowed_extensions:
            raise serializers.ValidationError(f"Image must be in one of the following formats: {', '.join(allowed_extensions)}")

        return value
    
    def get_username(self, obj):
        return obj.user.username
    


class GetClassMessagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassMessage
        fields = ['id', 'class_id', 'text', 'file', 'created_at', 'sender_id', 'edited'] 
        read_only_fields = ['id', 'class_id', 'file', 'created_at', 'sender_id', 'edited'] 

    