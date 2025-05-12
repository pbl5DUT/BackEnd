# api/models/project.py
from django.db import models
from api.models.user import User
from django.utils import timezone

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
    # Thay đổi từ auto_now_add=True thành default=timezone.now
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Tự động tạo project_id nếu chưa có
        if not self.project_id:
            # Lấy tất cả project_id hiện có từ database
            existing_ids = Project.objects.values_list('project_id', flat=True)
            
            # Tìm số lớn nhất từ các project_id hiện có
            max_id = 0
            for pid in existing_ids:
                try:
                    # Tách số từ 'prj-X'
                    id_num = int(pid.split('-')[1])
                    if id_num > max_id:
                        max_id = id_num
                except (IndexError, ValueError):
                    continue
            
            # Tạo project_id mới
            self.project_id = f'prj-{max_id + 1}'
            
            print(f"Tạo project_id mới: {self.project_id}")
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.project_name

    class Meta:
        db_table = 'api_project'