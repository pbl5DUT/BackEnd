import uuid

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from api.models.chatroom import ChatRoom, ChatRoomParticipant
from api.models.user import User
from api.serializers.chatroom_serializer import ChatRoomSerializer
from api.serializers.message_serializer import MessageSerializer


class ChatRoomViewSet(viewsets.ModelViewSet):       
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]

    def get_queryset(self):
        user = self.request.user
        return ChatRoom.objects.filter(participants=user)
    
    def create(self, request, *args, **kwargs):
        data = request.data
        user = request.user
        
        # Generate unique ID for the chat room
        chatroom_id = f"chat-{str(uuid.uuid4())[:8]}"
        
        # Create chat room
        chatroom = ChatRoom.objects.create(
            chatroom_id=chatroom_id,
            name=data.get('name', 'New Chat'),
            type=data.get('type', 'Private'),
            related_project_id=data.get('related_project_id'),
            related_team_id=data.get('related_team_id'),
            created_by=user
        )
        
        # Add creator as participant
        participant_id = f"part-{str(uuid.uuid4())[:8]}"
        ChatRoomParticipant.objects.create(
            id=participant_id,
            chatroom=chatroom,
            user=user,
            role='admin'
        )
        
        # Add other participants
        if 'participant_ids' in data and isinstance(data['participant_ids'], list):
            for user_id in data['participant_ids']:
                try:
                    participant = User.objects.get(user_id=user_id)
                    if participant != user:  # Don't add the creator twice
                        participant_id = f"part-{str(uuid.uuid4())[:8]}"
                        ChatRoomParticipant.objects.create(
                            id=participant_id,
                            chatroom=chatroom,
                            user=participant
                        )
                except User.DoesNotExist:
                    pass
        
        serializer = ChatRoomSerializer(chatroom, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        chatroom = self.get_object()
        messages = chatroom.messages.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)