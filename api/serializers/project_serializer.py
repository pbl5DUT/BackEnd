# api/serializers/project_serializer.py
from rest_framework import serializers
from api.models.project import Project

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['project_id', 'project_name', 'description', 'status', 'start_date', 'end_date', 'manager']
