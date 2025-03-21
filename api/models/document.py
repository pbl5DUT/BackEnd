# api/models/document.py

from django.db import models
from .user import User
from .project import Project

class Document(models.Model):
    document_id = models.AutoField(primary_key=True)
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50)
    uploaded_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    related_project = models.ForeignKey(Project, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name
