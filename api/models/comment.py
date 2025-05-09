# models/comment.py
from django.db import models
from api.models.user import User
from api.models.project import Project
from api.models.task import Task

class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    content = models.TextField()
    created_at = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    related_project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='comments')
    related_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name='general_comments')

    def __str__(self):
        return f"Comment by {self.created_by}"

    class Meta:
        db_table = 'api_comment'