# from django.db import models

# class WorkReport(models.Model):
#     TYPE_CHOICES = [
#         ('DAILY', 'Daily'),
#         ('WEEKLY', 'Weekly'),
#         ('MONTHLY', 'Monthly'),
#     ]
#     STATUS_CHOICES = [
#         ('DRAFT', 'Draft'),
#         ('SUBMITTED', 'Submitted'),
#         ('REVIEWED', 'Reviewed'),
#     ]
    
#     id = models.CharField(primary_key=True, max_length=50)
#     type = models.CharField(max_length=20, choices=TYPE_CHOICES)
#     title = models.CharField(max_length=255)
#     user_id = models.CharField(max_length=50)  # Sử dụng CharField thay vì ForeignKey
#     user_name = models.CharField(max_length=255)  # Thêm lại trường user_name
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
#     project_id = models.CharField(max_length=50, blank=True, null=True)
#     project_name = models.CharField(max_length=255, blank=True, null=True)
#     start_date = models.DateField()
#     end_date = models.DateField()
#     submitted_date = models.DateTimeField(blank=True, null=True)
#     reviewed_date = models.DateTimeField(blank=True, null=True)
#     reviewed_by = models.CharField(max_length=50, blank=True, null=True)
#     summary = models.TextField(blank=True, null=True)
#     challenges = models.TextField(blank=True, null=True)
#     next_steps = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.title

#     class Meta:
#         db_table = 'api_workreport'


from django.db import models
from api.models.user import User  # Import model User
from api.models.project import Project  # Import model Project
from api.models.task import Task  # Import model Task

class WorkReport(models.Model):
    TYPE_CHOICES = [
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
    ]
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('REVIEWED', 'Reviewed'),
    ]
    
    id = models.CharField(primary_key=True, max_length=50)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)

    # Khóa ngoại liên kết với model User (người tạo báo cáo công việc)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    # Khóa ngoại liên kết với model Project (dự án)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)

    # Khóa ngoại liên kết với nhiều Task (công việc)
    tasks = models.ManyToManyField(Task, blank=True, related_name='workreports')  # Liên kết với nhiều Task

 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    start_date = models.DateField()
    end_date = models.DateField()
    submitted_date = models.DateTimeField(blank=True, null=True)
    reviewed_date = models.DateTimeField(blank=True, null=True)
    reviewed_by = models.CharField(max_length=50, blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    challenges = models.TextField(blank=True, null=True)
    next_steps = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'api_workreport'
