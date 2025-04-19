from rest_framework import serializers
from api.models.project_user import ProjectUser
from api.serializers.user_serializer import UserSerializer

class ProjectUserSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = ProjectUser
        fields = ['user', 'role_in_project']
