# api/serializers/project_member_serializer.py
from rest_framework import serializers
from api.models.project_user import ProjectUser
from api.models.user import User
from api.models.project import Project
from datetime import date

class AddProjectMemberSerializer(serializers.Serializer):
    user_id = serializers.CharField(required=True)
    role_in_project = serializers.ChoiceField(
        choices=ProjectUser.ROLE_CHOICES,
        required=True
    )
    joined_date = serializers.DateField(required=False, default=date.today)
    
    def validate_user_id(self, value):
        try:
            User.objects.get(user_id=value)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("User không tồn tại")
    
    def create(self, validated_data):
        project = self.context['project']
        user = User.objects.get(user_id=validated_data['user_id'])
        role = validated_data['role_in_project']
        joined_date = validated_data.get('joined_date', date.today())
        
        # Kiểm tra xem thành viên đã tồn tại trong dự án chưa
        try:
            project_user = ProjectUser.objects.get(project=project, user=user)
            # Nếu đã tồn tại, cập nhật vai trò
            project_user.role_in_project = role
            project_user.save()
        except ProjectUser.DoesNotExist:
            # Tạo mới nếu chưa tồn tại
            project_user = ProjectUser(
                project=project,
                user=user,
                role_in_project=role,
                joined_date=joined_date
            )
            project_user.save()
            
        return project_user