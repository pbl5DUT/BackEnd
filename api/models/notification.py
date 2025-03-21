# api/models/notification.py

from django.db import models
from .user import User

class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    message = models.TextField()
    sent_to = models.ForeignKey(User, on_delete=models.CASCADE)
    sent_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message
