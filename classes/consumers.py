import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from .models import * 
from django.core.files.base import ContentFile
import jwt
from urllib.parse import parse_qs

class Consumer(AsyncWebsocketConsumer):
    async def connect(self):
        # self.user = self.scope["user"]
        self.class_id = self.scope['url_route']['kwargs']['class_id']
        self.group_name = f"online_class_{self.class_id}"
        query_string = parse_qs(self.scope['query_string'].decode())
        token = query_string.get('token', [None])[0]
        user = await self.get_user_from_jwt(token)
        
        if user is None:
            # If no user, close the connection
            await self.close(code=4001)
            return
        
        self.user = user 
        
       # Check if class exists
        if await self.is_class_exists(self.class_id) and await self.is_user_verified(self.user) and await self.is_user_enrolled(self.class_id, self.user):
            # Join class group if class exists
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()
        else:
            # Reject the connection if class does not exist or user not enrolled or verified
            await self.close(code=4001) 

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        print('disconnected')

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']

        if message_type == 'text':
            await self.handle_text_message(text_data_json)
        elif message_type in ['file', 'voice_message']:
            await self.handle_file_message(text_data_json, bytes_data)
        elif message_type == 'change_background':
            await self.handle_change_background(text_data_json)

    async def handle_text_message(self, data):
        sender_id = data['sender_id']
        message_text = data['message']
        # Save the message to model
        await self.save_message(sender_id, self.class_id, message_text)
        # Send message to group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',
                'message': message_text
            }
        )

    async def handle_file_message(self, data, bytes_data):
        sender_id = data['sender_id']
        class_id = data['class_id']
        file_type = data['type']  # 'file' or 'voice_message'
        
        # if 'bytes_data' contains the binary content of the file
        if bytes_data:
            file_message = await self.save_file_message(sender_id, class_id, bytes_data, file_type)
            if file_message:
                # Notify group about the new file
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'chat_message',
                        'message': f"New {file_type} uploaded.",
                        'file_url': file_message.file.url
                    }
                )
    
    # Handler for sending messages to the group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def handle_change_background(self, data):
        background_id = data['background_id']
        # Fetch the background image from the database
        background_image = await sync_to_async(self.get_background_image)(background_id)
        if background_image:
            # Send the background image URL to the client
            await self.send(text_data=json.dumps({
                'type': 'background_changed',
                'image_url': background_image.image.url
            }))
        else:
            # Handle case where background image is not found
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Background image not found'
            }))

    def get_background_image(self, background_id):
        try:
            return ClassBackgroundImage.objects.get(id=background_id)
        except ClassBackgroundImage.DoesNotExist:
            return None
        
        
    @database_sync_to_async
    def is_class_exists(self, class_id):
        return OnlineClass.objects.filter(id=class_id).exists()
    
    @database_sync_to_async
    def is_user_enrolled(self, class_id, user):
        if not user.is_authenticated:
            return False
        enrollment = ClassEnrollment.objects.filter(online_class_id=class_id, user=user)
        if enrollment.first().enrollment_status == 'Cancelled':
            return False
        return enrollment.exists()
    
    @database_sync_to_async
    def is_user_verified(self, user):
        if user.is_verified == 0:
           return False
        return True
    
    @database_sync_to_async
    def get_user_from_jwt(self, token):
        try:
            # Decode the token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            
            # Get the user from the payload
            user_id = payload.get('user_id')
            if user_id:
                return User.objects.get(id=user_id)
        except (jwt.ExpiredSignatureError, jwt.DecodeError, jwt.InvalidTokenError, User.DoesNotExist):
            return None
    
    @database_sync_to_async
    def save_message(self, sender_id, class_id, text):
        sender = User.objects.get(id=sender_id)  # Retrieve the sender user instance
        message = ClassMessage.objects.create(
            sender=sender, 
            class_id=class_id, 
            text=text
        )
        return message

    @database_sync_to_async
    def save_file_message(self, sender_id, class_id, bytes_data, file_type):
        sender = User.objects.get(id=sender_id)  # Retrieve the sender user instance
        message = ClassMessage(class_id=class_id, sender=sender)
        filename = f"{file_type}_{sender_id}_{message.created_at.strftime('%Y%m%d_%H%M%S')}.dat"
        message.file.save(filename, ContentFile(bytes_data))
        return message
    
    
    
