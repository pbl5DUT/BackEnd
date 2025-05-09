# models/document.py
from django.db import models
from api.models.user import User
from api.models.project import Project

class Document(models.Model):
    document_id = models.AutoField(primary_key=True)
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50)
    uploaded_at = models.DateTimeField()
    related_project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='documents')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_documents')

    def __str__(self):
        return self.file_name

    class Meta:
        db_table = 'api_document'