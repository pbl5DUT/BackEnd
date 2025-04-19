# api/models/project_user.py
from django.db import models
from api.models.project import Project
from api.models.user import User

class ProjectUser(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ROLE_CHOICES = [
        ('Manager', 'Manager'),
        ('Member', 'Member'),
        ('Support', 'Support'),
    ]
    role_in_project = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.full_name} - {self.role_in_project} in {self.project.project_name}"
