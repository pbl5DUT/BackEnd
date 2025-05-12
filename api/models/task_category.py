# api/models/task_category.py
from django.db import models
from api.models.project import Project

class TaskCategory(models.Model):
    id = models.CharField(primary_key=True, max_length=50)
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='categories',
        db_column='project_id'
    )
    tasks_count = models.IntegerField(default=0)
    completed_tasks_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Tự động tạo id nếu chưa có
        if not self.id:
            last_category = TaskCategory.objects.all().order_by('-id').first()
            if last_category:
                try:
                    last_id = int(last_category.id.split('-')[1])
                    self.id = f'cat-{last_id + 1}'
                except (IndexError, ValueError):
                    self.id = 'cat-1'
            else:
                self.id = 'cat-1'
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'api_taskcategory'