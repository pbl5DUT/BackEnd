import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, Message, User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        # Get user from scope (set by authentication middleware)
        self.user = self.scope.get('user')
        if not self.user or self.user.is_anonymous:
            await self.close()
            return
        
        # Check if user is in the chatroom
        chatroom_id = self.room_name.split('_')[1] if '_' in self.room_name else self.room_name
        is_participant = await self.is_participant(chatroom_id, self.user.user_id)
        
        if not is_participant:
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'chat_message':
                await self.handle_chat_message(data)
            elif message_type == 'mark_read':
                await self.handle_mark_read(data)
            elif message_type == 'typing':
                await self.handle_typing_indicator(data)
        except json.JSONDecodeError:
            pass
    
    async def handle_chat_message(self, data):
        # Process and save the message
        message = await self.save_message(data)
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )
    
    async def handle_mark_read(self, data):
        # Mark messages as read
        await self.mark_messages_read(data)
        
        # Send update to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'messages_read',
                'message_ids': data.get('message_ids', []),
                'user_id': data.get('user_id')
            }
        )
    
    async def handle_typing_indicator(self, data):
        # Send typing indicator to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'user_id': data.get('user_id'),
                'username': data.get('username', 'User'),
                'is_typing': data.get('is_typing', False)
            }
        )
    
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message']
        }))
    
    async def messages_read(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'messages_read',
            'message_ids': event['message_ids'],
            'user_id': event['user_id']
        }))
    
    async def typing_indicator(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user_id': event['user_id'],
            'username': event['username'],
            'is_typing': event['is_typing']
        }))
    
    @database_sync_to_async
    def is_participant(self, chatroom_id, user_id):
        try:
            chatroom = ChatRoom.objects.get(chatroom_id=chatroom_id)
            return chatroom.participants.filter(user_id=user_id).exists()
        except ChatRoom.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, data):
        # Create a new message
        import uuid
        message_id = f"msg-{str(uuid.uuid4())[:8]}"
        
        chatroom = ChatRoom.objects.get(chatroom_id=data.get('chatroom_id'))
        sender = User.objects.get(user_id=data.get('sender_id'))
        
        receiver = None
        if data.get('receiver_id'):
            try:
                receiver = User.objects.get(user_id=data.get('receiver_id'))
            except User.DoesNotExist:
                pass
        
        message = Message.objects.create(
            message_id=message_id,
            content=data.get('content'),
            chatroom=chatroom,
            sent_by=sender,
            receiver=receiver
        )
        
        # Manually serialize the message
        from api.serializers.message_serializer import MessageSerializer
        serializer = MessageSerializer(message)
        return serializer.data
    
    @database_sync_to_async
    def mark_messages_read(self, data):
        message_ids = data.get('message_ids', [])
        if message_ids:
            Message.objects.filter(message_id__in=message_ids).update(is_read=True)