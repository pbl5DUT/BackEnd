# api/models/message.py

from django.db import models
from .user import User
from .chatroom import ChatRoom

class Message(models.Model):
    message_id = models.AutoField(primary_key=True)
    content = models.TextField()
    sent_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')  # Thêm related_name
    receiver_id = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='received_messages')  # Thêm related_name
    sent_at = models.DateTimeField(auto_now_add=True)
    chatroom = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)

    def __str__(self):
        return self.content
