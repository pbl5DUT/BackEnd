

# api/models/project.py
from django.db import models
from api.models.user import User

class Project(models.Model):
    STATUS_CHOICES = [
        ('Planned', 'Planned'), 
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
    manager = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='managed_projects')
    
    # Sử dụng `related_name` để tránh xung đột với `manager`
    members = models.ManyToManyField(User, through='ProjectUser', related_name='projects')

    def __str__(self):
        return self.project_name

