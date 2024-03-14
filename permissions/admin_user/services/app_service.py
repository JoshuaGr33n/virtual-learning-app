# from repositories.repository import Repository
# from ..models import App
# from serializers import  *
# from rest_framework.response import Response
# from rest_framework import status
# from django.db import IntegrityError
# from django.http import Http404
# from django.core.exceptions import PermissionDenied

# class AppService:
    
#     def __init__(self):
#         self.repository = Repository(App)

#     def create_class(self, data, user):
#         serializer = AdminCreateClassSerializer(data=data)
#         if serializer.is_valid():
#             validated_data = serializer.validated_data
#             validated_data['user'] = user
#             try:
#                 app = self.repository.create(validated_data)
#                 return Response(AdminCreateClassSerializer(app).data, status=status.HTTP_201_CREATED)
#             except IntegrityError:
#                 return Response({'error': f'{validated_data["name"]} already exists under this user.'}, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
     
#     def get_apps_for_user(self, user):
#         apps = self.repository.filter_objects(user=user)
#         if apps.exists():
#             serializer = AppSerializer(apps, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         else:
#             return Response({'message': 'No apps created'}, status=status.HTTP_404_NOT_FOUND)
    
#     def get_app(self, user, app_id):
#         try:
#             app = self.repository.get_object(id=app_id, user=user)
#             serializer = AppSerializer(app) 
#             return serializer.data
#         except App.DoesNotExist:
#             raise Http404("App not found or does not belong to this user")
    
#     def update_app(self, user, app_id, update_data):
#         try:
#             app = self.repository.get_object(pk=app_id)
#         except App.DoesNotExist:
#             raise Http404('App not found.')

#         if app.user != user:
#             raise PermissionDenied('Permission denied. This app does not belong to this user.')

#         serializer = AppUpdateSerializer(app, data=update_data, partial=True)
#         if serializer.is_valid(raise_exception=True):
#             try:
#                 serializer.save()  
#                 response_data = {
#                 **serializer.data,  
#                 'message': 'App updated successfully.'
#                 }
#                 return response_data
#             except IntegrityError:
#                 return {'error': f"{update_data.get('name', app.name)} already exists under this user.", 'status': status.HTTP_400_BAD_REQUEST}
#         else:
#             return {'error': serializer.errors, 'status': status.HTTP_400_BAD_REQUEST}
    
    
#     def delete_app_and_subscriptions(self, user, app_id):
#             app = self.repository.get_object_or_fail(id=app_id, user=user)
#             if app is None:
#                 return "App not found.", 404

#             if app.user != user:
#                 return "Permission denied.", 403

#             app.delete()
#             return "App and corresponding subscriptions deleted successfully.", 204
