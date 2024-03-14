from rest_framework import status
from rest_framework.response import Response
from ..serializers import UserSerializer, LoginSerializer, AuthResponseSerializer
from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist

class UserService:
    @staticmethod
    def register(request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            response_serializer = AuthResponseSerializer(user)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    @staticmethod
    def login(request):
        # Create an instance of the LoginSerializer and validate request data
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data
            response_serializer = AuthResponseSerializer(user)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
    
    
    @staticmethod
    def userProfile(request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @staticmethod
    def logout_user(request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            # in case token does not exist
            pass
        # Perform the logout
        logout(request)
    


