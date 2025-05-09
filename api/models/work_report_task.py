# models/work_report_task.py
from django.db import models
from api.models.work_report import WorkReport

class WorkReportTask(models.Model):
    STATUS_CHOICES = [
        ('TODO', 'To Do'),
        ('IN_PROGRESS', 'In Progress'),
        ('DONE', 'Done'),
    ]
    
    id = models.CharField(primary_key=True, max_length=50)
    reportId = models.CharField(max_length=50)
    taskId = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    progress = models.IntegerField()
    timeSpent = models.FloatField()
    notes = models.TextField(blank=True, null=True)
    report = models.ForeignKey(WorkReport, on_delete=models.CASCADE, related_name='tasks')

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'api_workreporttask'