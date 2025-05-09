# models/notification.py
from django.db import models
from api.models.user import User

class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    message = models.TextField()
    sent_date = models.DateTimeField()
    sent_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')

    def __str__(self):
        return f"Notification to {self.sent_to}"

    class Meta:
        db_table = 'api_notification'