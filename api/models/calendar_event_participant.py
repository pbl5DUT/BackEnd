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
    eventId = models.CharField(max_length=50)
    userId = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    event = models.ForeignKey(Calendar, on_delete=models.CASCADE, related_name='participants')

    def __str__(self):
        return f"Participant in {self.eventId}"

    class Meta:
        db_table = 'api_calendareventparticipant'