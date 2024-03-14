from repositories.repository import Repository
from classes.models import *
from identity.models import User
from ..serializers import  *
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError
from django.http import Http404
from django.core.exceptions import PermissionDenied

class AdminService:
    
    def __init__(self):
        self.model = User
        self.repository = Repository(self.model)
        

    def get_all_users(self, filters):
        users = self.repository.filters(is_admin=False, **filters)
        if users.exists():
            serializer = AdminManageUserProfileSerializer(users, many=True)
            return serializer.data 
        else:
            return [] 