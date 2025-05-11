from django.db import models
from .user import User
from .chatroom import ChatRoom  # Import ChatRoom model instead of redefining it

class Message(models.Model):
    message_id = models.CharField(primary_key=True, max_length=50)
    content = models.TextField(null=True, blank=True)
    attachment_url = models.CharField(max_length=255, null=True, blank=True)
    attachment_type = models.CharField(max_length=50, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)
    chatroom = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sent_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_messages')
    
    class Meta:
        db_table = 'api_message'
        ordering = ['sent_at']