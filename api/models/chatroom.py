from django.db import models
from .user import User
from .project import Project

class ChatRoom(models.Model):
    chatroom_id = models.CharField(primary_key=True, max_length=50)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50)  # 'Project', 'Private', etc.
    related_project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='chatrooms')
    related_team_id = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_chatrooms')
    participants = models.ManyToManyField(User, through='ChatRoomParticipant', related_name='chatrooms')
    
    class Meta:
        db_table = 'api_chatroom'
        ordering = ['-created_at']

class ChatRoomParticipant(models.Model):
    id = models.CharField(primary_key=True, max_length=50)
    chatroom = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=50, default='member')
    
    class Meta:
        db_table = 'api_chatroomparticipant'
        unique_together = ('chatroom', 'user')