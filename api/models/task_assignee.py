# models/task_assignee.py
from django.db import models
from api.models.user import User
from api.models.task import Task

class TaskAssignee(models.Model):
    id = models.BigAutoField(primary_key=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='assignees')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_assignments')
    assigned_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'api_taskassignee'

    def __str__(self):
        return f"{self.user} assigned to {self.task}"