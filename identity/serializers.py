from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import *
import random
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['first_name', 'last_name','gender', 'country', 'password1', 'password2', 'email']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
       
        otp = random.randint(111111, 999999)
        profile, created = User_OTP.objects.get_or_create(user=user)
        profile.set_otp(otp)
        return user
    
    def validate_password1(self, value):
        validate_password(value)
        return value
    
    def validate(self, data):
        # Validate that the two passwords match
        if data['password1'] != data['password2']:
            raise serializers.ValidationError({"password": "The two password fields didn't match."})
        return data

    def create(self, validated_data):
        # Remove password1 and password2 from validated_data
        validated_data.pop('password1')
        password = validated_data.pop('password2')

        # Automatically generate a unique username
        username = self.generate_unique_username(validated_data['first_name'])

        # Create the user
        user = User.objects.create_user(username=username, password=password, **validated_data)

        otp = random.randint(111111, 999999)
        profile, created = User_OTP.objects.get_or_create(user=user)
        profile.set_otp(otp, type="Login")

        return user

    def generate_unique_username(self, first_name):
        while True:
            random_digits = random.randint(100000, 999999)
            username = f"{first_name}{random_digits}"
            if not User.objects.filter(username=username).exists():
                return username


class RegenerateOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        # Retrieve user by email
        user = get_object_or_404(User, email=data['email'])
        if user.is_verified == False:
            data['user'] = user
            return data
        else:
            raise serializers.ValidationError("This account is already verified!")

    def save(self, **kwargs):
        user = self.validated_data['user']
        new_otp = get_random_string(length=6, allowed_chars='1234567890')
        user_otp, created = User_OTP.objects.get_or_create(user=user)
        user_otp.set_otp(new_otp, type="Login")
        self.validated_data['new_otp'] = new_otp
        return self.validated_data            

class UserLoginSerializer(serializers.Serializer):
        username = serializers.CharField()
        password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)

        def validate(self, data):
            username = data.get('username')
            password = data.get('password')

            if username and password:
                user = authenticate(request=self.context.get('request'), username=username, password=password)

                if not user:
                    msg = 'Unable to log in with provided credentials.'
                    raise serializers.ValidationError(msg, code='authorization')
                else:
                    if user.is_verified == False:
                        raise serializers.ValidationError("This account is not verified!")
            else:
                msg = 'Must include "username" and "password".'
                raise serializers.ValidationError(msg, code='authorization')

            data['user'] = user
            return data    
        
        

class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('context', {})
        super(ForgetPasswordSerializer, self).__init__(*args, **kwargs)

    def validate_email(self, value):
        user = User.objects.filter(email=value).first()
        if not user:
            raise serializers.ValidationError("Email does not exist in our database.")
        otp = random.randint(100000, 999999)
        if hasattr(user, 'user_otp'):
            user.user_otp.set_otp(otp, type='Password')
        else:
            User_OTP.objects.create(user=user, otp=otp,otp_type='Password',otp_expiry=timezone.now() + datetime.timedelta(minutes=5))             
        self.context['otp'] = otp
        return value

    def create(self, validated_data):
        validated_data['otp'] = self.otp
        return validated_data
    

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.IntegerField()
    password1 = serializers.CharField(label='New Password', write_only=True, style={'input_type': 'password'})
    password2 = serializers.CharField(label='New Confirm Password', write_only=True, style={'input_type': 'password'})

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
            self.context['user'] = user
        except User.DoesNotExist:
            raise serializers.ValidationError("Email does not exist.")
        return value

    def validate_otp(self, value):
        self.context['otp_to_verify'] = value
        return value

    def validate_password1(self, value):
        validate_password(value)
        return value

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")

        user = self.context.get('user')
        otp_to_verify = self.context.get('otp_to_verify')
        if not (hasattr(user, 'user_otp') and user.user_otp.verify_otp(otp_to_verify, type="Password")):
            raise serializers.ValidationError("Invalid or expired OTP.")
       
        return data
    


