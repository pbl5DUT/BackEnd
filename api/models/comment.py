# api/models/comment.py

from django.db import models
from .user import User
from .project import Project
from .task import Task

class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    related_project = models.ForeignKey(Project, blank=True, null=True, on_delete=models.CASCADE)
    related_task = models.ForeignKey(Task, blank=True, null=True, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.content
