from django.db import models
from api.models.user import User
from api.models.project import Project
from api.models.task_category import TaskCategory
import uuid

class Task(models.Model):
    STATUS_CHOICES = [
        ('Todo', 'Todo'),
        ('In Progress', 'In Progress'),
        ('Review', 'Review'),
        ('Done', 'Done'),
    ]
    
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Urgent', 'Urgent'),
    ]
    
    task_id = models.CharField(primary_key=True, max_length=50)
    task_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Todo')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    start_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    actual_end_date = models.DateField(blank=True, null=True)
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        db_column='assignee_id'
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks',
        db_column='project_id'
    )
    category = models.ForeignKey(
        TaskCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
        db_column='category_id'
    )
    category_name = models.CharField(max_length=255, blank=True, null=True)
    progress = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Tạo task_id duy nhất nếu chưa có
        if not self.task_id:
            self.task_id = f"task-{uuid.uuid4().hex[:8]}"

        # Cập nhật category_name nếu có category
        if self.category and not self.category_name:
            self.category_name = self.category.name
            
        # Nếu trạng thái là Done thì set progress = 100
        if self.status == 'Done' and self.progress != 100:
            self.progress = 100
            
        super().save(*args, **kwargs)

        # Cập nhật lại số lượng task trong category
        if self.category:
            total_tasks = Task.objects.filter(category=self.category).count()
            completed_tasks = Task.objects.filter(category=self.category, status='Done').count()
            self.category.tasks_count = total_tasks
            self.category.completed_tasks_count = completed_tasks
            self.category.save()

    def __str__(self):
        return self.task_name

    class Meta:
        db_table = 'api_task'
