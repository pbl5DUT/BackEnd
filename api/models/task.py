# api/models/task.py

from django.db import models
from .user import User
from .project import Project

class Task(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]
    
    task_id = models.AutoField(primary_key=True)
    task_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(choices=STATUS_CHOICES, default='Pending', max_length=20)
    deadline = models.DateField(blank=True, null=True)
    assignee = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.task_name
