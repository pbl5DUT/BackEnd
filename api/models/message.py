# models/message.py
from django.db import models
from api.models.user import User
from api.models.chatroom import ChatRoom

class Message(models.Model):
    message_id = models.AutoField(primary_key=True)
    content = models.TextField()
    sent_at = models.DateTimeField()
    chatroom = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    receiver_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='received_messages')
    sent_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')

    def __str__(self):
        return f"Message in {self.chatroom} by {self.sent_by}"

    class Meta:
        db_table = 'api_message'