from django.shortcuts import render
from .services.class_service import *
from rest_framework.permissions import IsAuthenticated
from permissions.permissions import *
from rest_framework.views import APIView
import logging


class AllClassesView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]
    def get(self, request, *args, **kwargs):
        class_service = ClassService()
        classes_data = class_service.get_all_classes()
        if classes_data:
            return Response(classes_data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'No classes created'}, status=status.HTTP_404_NOT_FOUND)
        

class GetClassView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]
    def get(self, request, class_id, *args, **kwargs):
        class_service = ClassService()
        try:
            response_data = class_service.get_class(class_id)
            return Response(response_data) 
        except Http404 as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)


class ClassBackgroundImageView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]
    
    def get(self, request, *args, **kwargs):
        class_service = ClassService()
        try:
            response_data = class_service.get_background(request.user)
            return Response(response_data) 
        except Http404 as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)


    def post(self, request):
        serializer = ClassBackgroundImageSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            service = ClassService()
            data = serializer.validated_data
            data.pop('user', None)
            background_image = service.add_or_update_background(request.user, data)
            return Response(ClassBackgroundImageSerializer(background_image).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # put = post        


class ClassMessagesView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]
    def get(self, request, class_id, *args, **kwargs):
        class_service = ClassService()
        try:
            messages = class_service.get_class_messages(class_id)
            if messages:
                return Response(messages, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'No messages'}, status=status.HTTP_404_NOT_FOUND)
        except Http404 as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)

            
class ClassSingleMessageView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]
    def get(self, request, class_id, message_id, *args, **kwargs):
        class_service = ClassService()
        
        # logger = logging.getLogger(__name__)
        try:
            response_data = class_service.get_single_message(request.user, class_id, message_id)
            return Response(response_data) 
        except Http404 as e:
            # logger.error(e, exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    
    def put(self, request, class_id, message_id, *args, **kwargs):
        service = ClassService()
        try:
            message = service.get_single_message(request.user, class_id, message_id)
            serializer = GetClassMessagesSerializer(message, data=request.data)
            if serializer.is_valid(raise_exception=True):
                data = serializer.validated_data
                updated_message = service.edit_message(class_id, message_id, data)
                return Response(GetClassMessagesSerializer(updated_message).data)
        except Http404 as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, class_id, message_id, *args, **kwargs):
        service = ClassService()
        try:
            service.get_single_message(request.user, class_id, message_id)
            service.delete_message(class_id, message_id)
            return Response({"message": "Message deleted successfully."}, status=status.HTTP_200_OK)
        except Http404 as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)


class AdminClearAllClassMessagesView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    def delete(self, request, class_id, *args, **kwargs):
        class_service = ClassService()
        try:
            class_service.clear_all_class_messages(class_id)
            return Response({"message": "Messages deleted successfully."}, status=status.HTTP_200_OK)
        except Http404 as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
