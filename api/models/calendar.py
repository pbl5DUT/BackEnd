# models/calendar.py
from django.db import models

class Calendar(models.Model):
    TYPE_CHOICES = [
        ('MEETING', 'Meeting'),
        ('DEADLINE', 'Deadline'),
        ('REMINDER', 'Reminder'),
        ('OTHER', 'Other'),
    ]
    
    event_id = models.CharField(primary_key=True, max_length=50)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    projectId = models.CharField(max_length=50, blank=True, null=True)
    userId = models.CharField(max_length=50)
    location = models.CharField(max_length=255, blank=True, null=True)
    isAllDay = models.BooleanField(default=False)
    createdAt = models.DateTimeField()
    updatedAt = models.DateTimeField()

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'api_calendar'