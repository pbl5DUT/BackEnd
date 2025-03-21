# api/models/report.py

from django.db import models
from .user import User

class Report(models.Model):
    report_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    submitted_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    submitted_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
