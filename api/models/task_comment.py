# models/task_comment.py
from django.db import models
from api.models.user import User
from api.models.task import Task

class TaskComment(models.Model):
    id = models.BigAutoField(primary_key=True)
    content = models.TextField()
    created_at = models.DateTimeField()
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_comments')
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='replies')

    class Meta:
        db_table = 'api_taskcomment'

    def __str__(self):
        return f"Comment by {self.user} on {self.task}"