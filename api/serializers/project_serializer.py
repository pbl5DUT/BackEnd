# api/serializers/project_serializer.py
from rest_framework import serializers
from api.models.project import Project
from api.models.project_user import ProjectUser
from api.models.user import User
from api.serializers.user_serializer import UserSerializer


class ProjectSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()
    manager = UserSerializer(read_only=True)  # Hiển thị thông tin đầy đủ của manager
    manager_id = serializers.CharField(write_only=True, required=False)  # Trường để nhập manager_id
    members_count = serializers.SerializerMethodField()  # Thêm số lượng members

    class Meta:
        model = Project
        fields = [
            'project_id', 'project_name', 'description', 'status',
            'start_date', 'end_date', 'manager', 'manager_id',
            'progress', 'created_at', 'updated_at', 'members', 'members_count'
        ]   
        extra_kwargs = {
            'project_id': {'required': False},
            'progress': {'required': False},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }

    def get_members_count(self, obj):
        """Đếm số lượng members"""
        return getattr(obj, 'members_count', ProjectUser.objects.filter(project=obj).count())

    def get_members(self, obj):
        """
        Lấy danh sách members của project
        Sử dụng lazy import để tránh circular import
        """
        # Lazy import để tránh circular import
        from api.serializers.project_user_serializer import ProjectUserSerializer
        
        # Tối ưu query với select_related
        project_users = ProjectUser.objects.filter(project=obj).select_related('user', 'project')
        return ProjectUserSerializer(project_users, many=True).data

    def create(self, validated_data):
        """Tạo project mới"""
        # Xử lý manager_id nếu được cung cấp
        manager_id = validated_data.pop('manager_id', None)
        
        if manager_id:
            try:
                manager = User.objects.get(user_id=manager_id)
                validated_data['manager'] = manager
            except User.DoesNotExist:
                raise serializers.ValidationError({
                    'manager_id': f'Manager với ID "{manager_id}" không tồn tại'
                })
            
        # Tạo dự án
        project = Project.objects.create(**validated_data)
        
        return project
    
    def update(self, instance, validated_data):
        """Cập nhật project"""
        # Xử lý manager_id nếu được cung cấp
        manager_id = validated_data.pop('manager_id', None)
        
        if manager_id:
            try:
                instance.manager = User.objects.get(user_id=manager_id)
            except User.DoesNotExist:
                raise serializers.ValidationError({
                    'manager_id': f'Manager với ID "{manager_id}" không tồn tại'
                })
        
        # Cập nhật các trường khác
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

    def to_representation(self, instance):
        """
        Tùy chỉnh output representation
        Có thể điều chỉnh dựa trên context
        """
        data = super().to_representation(instance)
        
        # Nếu context yêu cầu, có thể ẩn members để tăng performance
        request = self.context.get('request')
        if request and request.query_params.get('include_members') == 'false':
            data.pop('members', None)
        
        return data


class ProjectListSerializer(ProjectSerializer):
    """
    Serializer tối ưu cho list view (không load members)
    Sử dụng cho endpoint GET /api/projects/
    """
    class Meta(ProjectSerializer.Meta):
        fields = [
            'project_id', 'project_name', 'description', 'status',
            'start_date', 'end_date', 'manager', 'progress', 
            'created_at', 'updated_at', 'members_count'
        ]

    def get_members(self, obj):
        """Override để không load members trong list view"""
        return []


class ProjectDetailSerializer(ProjectSerializer):
    """
    Serializer đầy đủ cho detail view
    Sử dụng cho endpoint GET /api/projects/{id}/
    """
    pass  # Sử dụng toàn bộ fields từ ProjectSerializer