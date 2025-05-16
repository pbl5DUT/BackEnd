# models/calendar_event_participant.py
from django.db import models
from api.models.calendar import Calendar

class CalendarEventParticipant(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('DECLINED', 'Declined'),
    ]
    
    id = models.CharField(primary_key=True, max_length=50)
    user_id = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    event = models.ForeignKey(Calendar, on_delete=models.CASCADE, related_name='participants')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Participant in {self.event_id}"

    class Meta:
        db_table = 'api_calendareventparticipant'
