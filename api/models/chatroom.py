# models/chatroom.py
from django.db import models
from api.models.user import User

class ChatRoom(models.Model):
    chatroom_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_chatrooms')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'api_chatroom'