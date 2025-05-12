# models/task_attachment.py
from django.db import models
from api.models.user import User
from api.models.task import Task

class TaskAttachment(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    file_url = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50)
    file_size = models.IntegerField()
    uploaded_at = models.DateTimeField()
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_attachments')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments')

    class Meta:
        db_table = 'api_taskattachment'

    def __str__(self):
        return self.name