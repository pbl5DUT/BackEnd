from rest_framework import serializers
from api.models import Calendar,CalendarEventParticipant

class CalendarEventParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarEventParticipant
        fields = ['id', 'user_id', 'status', 'created_at']


class CalendarSerializer(serializers.ModelSerializer):
    participants = CalendarEventParticipantSerializer(many=True, read_only=True)

    class Meta:
        model = Calendar
        fields = [
            'event_id', 'title', 'description', 'start', 'end', 'type',
            'project_id', 'user_id', 'location', 'is_all_day', 'created_at', 'updated_at',
            'participants',
        ]