import uuid
import os
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings

from api.models.message import Message
from api.models.chatroom import ChatRoom
from api.models.user import User
from api.serializers.message_serializer import MessageSerializer

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    def create(self, request, *args, **kwargs):
        data = request.data
        user = request.user
        
        # Get chatroom ID from either 'chatroom' or 'chatroom_id' field
        chatroom_id = data.get('chatroom_id') or data.get('chatroom')
        if not chatroom_id:
            return Response({"error": "Chatroom ID is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Handle different chatroom ID formats (chat_ vs chat-)
        if chatroom_id and chatroom_id.startswith('chat_'):
            chatroom_id = chatroom_id.replace('chat_', 'chat-')
        
        try:
            chatroom = ChatRoom.objects.get(chatroom_id=chatroom_id)
            
            # Check if user is participant in the chat room
            if not chatroom.participants.filter(user_id=user.user_id).exists():
                return Response({"error": "You are not a participant in this chat room"}, 
                                status=status.HTTP_403_FORBIDDEN)
            
            # Create message
            message_id = f"msg-{str(uuid.uuid4())[:8]}"
            
            # Optional receiver
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
                sent_by=user,
                receiver=receiver,
                attachment_url=data.get('attachment_url'),
                attachment_type=data.get('attachment_type')
            )
            
            serializer = MessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_201_CREATED)        
        except ChatRoom.DoesNotExist:
            return Response({"error": f"Chatroom with ID {chatroom_id} does not exist"}, 
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_attachment(self, request):
        file_obj = request.FILES.get('file')
        chatroom_id = request.data.get('chatroom_id')
        receiver_id = request.data.get('receiver_id')
        
        if not file_obj or not chatroom_id:
            return Response({"error": "File and chatroom_id are required"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            chatroom = ChatRoom.objects.get(chatroom_id=chatroom_id)
            
            # Get file type from file extension
            file_name = file_obj.name
            file_extension = file_name.split('.')[-1].lower() if '.' in file_name else ''
            
            # Determine attachment type based on extension
            attachment_type = 'image'
            if file_extension in ['mp4', 'avi', 'mov', 'wmv']:
                attachment_type = 'video'
            elif file_extension in ['doc', 'docx', 'pdf', 'txt', 'xls', 'xlsx', 'ppt', 'pptx']:
                attachment_type = 'document'
                
            # Create attachments directory under MEDIA_ROOT
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'attachments')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate unique filename
            unique_filename = f"{uuid.uuid4().hex[:8]}_{file_name}"
            
            # Save file relative to MEDIA_ROOT
            file_path = f"attachments/{unique_filename}"
            full_path = os.path.join(settings.MEDIA_ROOT, 'attachments', unique_filename)
            
            # Save file
            with open(full_path, 'wb+') as destination:
                for chunk in file_obj.chunks():
                    destination.write(chunk)
            
            # Create URL path with forward slashes
            attachment_url = f"{settings.MEDIA_URL.rstrip('/')}/attachments/{unique_filename}"
            
            # Create message with appropriate content based on attachment type
            message_id = f"msg-{str(uuid.uuid4())[:8]}"
            
            # Create content based on attachment type
            if attachment_type == 'image':
                content = f'<img src="{attachment_url}" alt="{file_name}" style="max-width: 100%; max-height: 300px;" />'
            elif attachment_type == 'video':
                content = f'<video controls style="max-width: 100%;"><source src="{attachment_url}" type="video/{file_extension}"></video>'
            else:
                content = f'<a href="{attachment_url}" target="_blank" download="{file_name}"><i class="document-icon"></i> {file_name}</a>'
            
            message = Message.objects.create(
                message_id=message_id,
                chatroom=chatroom,
                sent_by=request.user,
                content=content,
                attachment_url=attachment_url,
                attachment_type=attachment_type
            )
            
            # Handle receiver if provided
            if receiver_id:
                try:
                    receiver = User.objects.get(user_id=receiver_id)
                    message.receiver = receiver
                    message.save()
                except User.DoesNotExist:
                    pass
            
            serializer = self.get_serializer(message)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except ChatRoom.DoesNotExist:
            return Response({"error": "Chat room not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            import traceback
            print(f"Error uploading file: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {"error": f"Error uploading file: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )