# models/work_report.py
from django.db import models

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
    userId = models.CharField(max_length=50)
    userName = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    projectId = models.CharField(max_length=50, blank=True, null=True)
    projectName = models.CharField(max_length=255, blank=True, null=True)
    startDate = models.DateField()
    endDate = models.DateField()
    submittedDate = models.DateTimeField(blank=True, null=True)
    reviewedDate = models.DateTimeField(blank=True, null=True)
    reviewedBy = models.CharField(max_length=50, blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    challenges = models.TextField(blank=True, null=True)
    nextSteps = models.TextField(blank=True, null=True)
    createdAt = models.DateTimeField()
    updatedAt = models.DateTimeField()

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'api_workreport'