# models/project.py
from django.db import models
from api.models.user import User

class Project(models.Model):
    STATUS_CHOICES = [
        ('Not Started', 'Not Started'),
        ('Ongoing', 'Ongoing'),
        ('On Hold', 'On Hold'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    
    project_id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='managed_projects')
    progress = models.IntegerField(default=0)  # Tiến độ dự án, giá trị từ 0-100

    def __str__(self):
        return self.project_name

    class Meta:
        db_table = 'api_project'