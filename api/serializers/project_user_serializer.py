# api/serializers/project_user_serializer.py
from rest_framework import serializers
from api.models.project_user import ProjectUser
from api.serializers.user_serializer import UserSerializer

class ProjectUserSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    joined_date = serializers.DateField(required=False)

    class Meta:
        model = ProjectUser
        fields = ['id', 'user', 'role_in_project', 'joined_date', 'created_at']