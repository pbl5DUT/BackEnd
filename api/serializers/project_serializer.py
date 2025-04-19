from rest_framework import serializers
from api.models.project import Project
from api.models.project_user import ProjectUser
from .project_user_serializer import ProjectUserSerializer
from api.models.user import User

class ProjectSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()
    manager = serializers.StringRelatedField()  # ← sửa ở đây

    class Meta:
        model = Project
        fields = [
            'project_id', 'project_name', 'description', 'status',
            'start_date', 'end_date', 'manager', 'members'
        ]

    def get_members(self, obj):
        project_users = ProjectUser.objects.filter(project=obj)
        return ProjectUserSerializer(project_users, many=True).data
