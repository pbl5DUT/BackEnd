# api/models/project_user.py
from django.db import models
from api.models.project import Project
from api.models.user import User

class ProjectUser(models.Model):
    ROLE_CHOICES = [
        ('Manager', 'Manager'),
        ('Member', 'Member'),
        ('Support', 'Support'),
        ('Observer', 'Observer'),
        ('Developer', 'Developer'),  
        ('Tester', 'Tester'),   
    ]

    id = models.CharField(primary_key=True, max_length=50)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_assignments')
    role_in_project = models.CharField(max_length=20, choices=ROLE_CHOICES)
    joined_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Tự động tạo id nếu chưa có
        if not self.id:
            last_project_user = ProjectUser.objects.all().order_by('-id').first()
            if last_project_user:
                try:
                    last_id = int(last_project_user.id.split('-')[1])
                    self.id = f'prju-{last_id + 1}'
                except (IndexError, ValueError):
                    self.id = 'prju-1'
            else:
                self.id = 'prju-1'
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.full_name} - {self.role_in_project} in {self.project.project_name}"

    class Meta:
        db_table = 'api_projectuser'
        unique_together = ('project', 'user')