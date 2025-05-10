# api/serializers/project_serializer.py
from rest_framework import serializers
from api.models.project import Project
from api.models.project_user import ProjectUser
from .project_user_serializer import ProjectUserSerializer
from api.models.user import User
from api.serializers.user_serializer import UserSerializer

class ProjectSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()
    manager = UserSerializer(read_only=True)  # Hiển thị thông tin đầy đủ của manager
    manager_id = serializers.CharField(write_only=True, required=False)  # Trường để nhập manager_id

    class Meta:
        model = Project
        fields = [
            'project_id', 'project_name', 'description', 'status',
            'start_date', 'end_date', 'manager', 'manager_id',
            'progress', 'created_at', 'updated_at', 'members'
        ]
        extra_kwargs = {
            'project_id': {'required': False},
            'progress': {'required': False},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }

    def get_members(self, obj):
        # Sử dụng related_name 'project_members' nếu đã thêm vào model
        project_users = ProjectUser.objects.filter(project=obj)
        return ProjectUserSerializer(project_users, many=True).data

    def create(self, validated_data):
        # Xử lý manager_id nếu được cung cấp
        manager_id = validated_data.pop('manager_id', None)
        
        if manager_id:
            try:
                manager = User.objects.get(user_id=manager_id)
            except User.DoesNotExist:
                raise serializers.ValidationError({'manager_id': 'Manager không tồn tại'})
        else:
            manager = None
            
        # Tạo dự án
        project = Project(manager=manager, **validated_data)
        project.save()
        
        return project
    
    def update(self, instance, validated_data):
        # Xử lý manager_id nếu được cung cấp
        manager_id = validated_data.pop('manager_id', None)
        
        if manager_id:
            try:
                instance.manager = User.objects.get(user_id=manager_id)
            except User.DoesNotExist:
                raise serializers.ValidationError({'manager_id': 'Manager không tồn tại'})
        
        # Cập nhật các trường khác
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance