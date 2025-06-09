import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

User = get_user_model()

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('Info', 'Info'),
        ('Warning', 'Warning'),
        ('Alert', 'Alert'),
        ('Success', 'Success'),
    ]

    notification_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, default='Info')
    is_read = models.BooleanField(default=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.CharField(max_length=50, null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    sent_date = models.DateTimeField(auto_now_add=True)
    sent_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')

    def __str__(self):
        return f"{self.type} Notification to {self.sent_to} - {self.title}"

    class Meta:
        db_table = 'api_notification'
