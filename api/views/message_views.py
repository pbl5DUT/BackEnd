import uuid
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

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
        
        try:
            chatroom = ChatRoom.objects.get(chatroom_id=data.get('chatroom'))
            
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
                receiver=receiver
            )
            
            serializer = MessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except ChatRoom.DoesNotExist:
            return Response({"error": "Chat room not found"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_attachment(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        chatroom_id = request.data.get('chatroom_id')
        try:
            chatroom = ChatRoom.objects.get(chatroom_id=chatroom_id)
        except ChatRoom.DoesNotExist:
            return Response({"error": "Chat room not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Handle file upload logic here (save to S3, local storage, etc.)
        # For simplicity, we're just creating a message with attachment info
        
        message_id = f"msg-{str(uuid.uuid4())[:8]}"
        
        # Determine attachment type based on file extension
        filename = file.name.lower()
        attachment_type = 'document'  # Default
        if filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            attachment_type = 'image'
        elif filename.endswith(('.mp3', '.wav', '.ogg')):
            attachment_type = 'audio'
        elif filename.endswith(('.mp4', '.mov', '.avi')):
            attachment_type = 'video'
        
        # Save file and get URL (assuming you have a file storage configuration)
        # file_url = your_storage_handler.save(file)
        
        # For demo purposes, we'll just use a placeholder
        file_url = f"/media/attachments/{file.name}"
        
        # Optional receiver
        receiver = None
        if request.data.get('receiver_id'):
            try:
                receiver = User.objects.get(user_id=request.data.get('receiver_id'))
            except User.DoesNotExist:
                pass
        
        message = Message.objects.create(
            message_id=message_id,
            content=f"Sent an attachment: {file.name}",
            attachment_url=file_url,
            attachment_type=attachment_type,
            chatroom=chatroom,
            sent_by=request.user,
            receiver=receiver
        )
        
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)