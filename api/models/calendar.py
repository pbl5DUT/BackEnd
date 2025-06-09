# models/calendar.py
from django.db import models

class Calendar(models.Model):
    TYPE_CHOICES = [
        ('MEETING', 'MEETING'),
        ('DEADLINE', 'DEADLINE'),
        ('TASK', 'TASK'),
        ('OTHER', 'OTHER'),
    ]
    event_id = models.CharField(primary_key=True, max_length=50)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    project_id = models.CharField(max_length=50, blank=True, null=True)
    user_id = models.CharField(max_length=50)
    location = models.CharField(max_length=255, blank=True, null=True)
    is_all_day = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)  # tự động set khi tạo
    updated_at = models.DateTimeField(auto_now=True)      # tự động cập nhật khi lưu

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'api_calendar'