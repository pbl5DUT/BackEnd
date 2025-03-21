# api/models/chatroom.py

from django.db import models
from .user import User

class ChatRoom(models.Model):
    chatroom_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)  # Thêm null=True
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
