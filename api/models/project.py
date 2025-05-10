# api/models/project.py
from django.db import models
from api.models.user import User

class Project(models.Model):
    STATUS_CHOICES = [
        ('Planning', 'Planning'),
        ('In Progress', 'In Progress'),
        ('On Hold', 'On Hold'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    project_id = models.CharField(primary_key=True, max_length=50)
    project_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='Planning'
    )
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    manager = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='managed_projects',
        db_column='manager_id'
    )
    progress = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Tự động tạo project_id nếu chưa có
        if not self.project_id:
            last_project = Project.objects.all().order_by('-project_id').first()
            if last_project:
                try:
                    last_id = int(last_project.project_id.split('-')[1])
                    self.project_id = f'prj-{last_id + 1}'
                except (IndexError, ValueError):
                    self.project_id = 'prj-1'
            else:
                self.project_id = 'prj-1'
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.project_name

    class Meta:
        db_table = 'api_project'