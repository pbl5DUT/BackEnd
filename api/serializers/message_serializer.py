from rest_framework import serializers
from api.models.message import Message
from api.serializers.user_serializer import UserSerializer

class MessageSerializer(serializers.ModelSerializer):
    sent_by = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['message_id', 'content', 'attachment_url', 'attachment_type', 
                 'is_read', 'sent_at', 'chatroom', 'sent_by', 'receiver']