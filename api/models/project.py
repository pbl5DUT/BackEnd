# api/models/project.py

from django.db import models
from .user import User

class Project(models.Model):
    STATUS_CHOICES = [
        ('Ongoing', 'Ongoing'),
        ('Completed', 'Completed'),
        ('On Hold', 'On Hold'),
    ]
    
    project_id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(choices=STATUS_CHOICES, default='Ongoing', max_length=20)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    manager = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    
    def __str__(self):
        return self.project_name
