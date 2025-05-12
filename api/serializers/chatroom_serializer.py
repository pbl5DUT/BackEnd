from rest_framework import serializers
from api.models.chatroom import ChatRoom, ChatRoomParticipant
from api.models.user import User
from api.serializers.user_serializer import UserSerializer

class ChatRoomParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ChatRoomParticipant
        fields = ['id', 'user', 'joined_at', 'role']

class ChatRoomSerializer(serializers.ModelSerializer):
    participants = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = ['chatroom_id', 'name', 'type', 'related_project', 'related_team_id', 
                 'created_at', 'participants', 'last_message', 'unread_count']
    
    def get_participants(self, obj):
        participants = ChatRoomParticipant.objects.filter(chatroom=obj)
        return ChatRoomParticipantSerializer(participants, many=True).data
    
    def get_last_message(self, obj):
        from api.serializers.message_serializer import MessageSerializer
        try:
            last_message = obj.messages.latest('sent_at')
            return MessageSerializer(last_message).data
        except:
            return None
    
    def get_unread_count(self, obj):
        user = self.context.get('request').user
        return obj.messages.filter(is_read=False).exclude(sent_by=user).count()