from rest_framework import serializers
from api.models.task import Task
from api.models.user import User
from api.models.project import Project
from api.models.task_category import TaskCategory
from api.serializers.user_serializer import UserSerializer

class TaskSerializer(serializers.ModelSerializer):
    assignee = UserSerializer(read_only=True)  # Hiển thị thông tin chi tiết của người được giao
    assignee_id = serializers.CharField(write_only=True, required=False)  # Cho phép nhập user_id dạng chuỗi
    category_name = serializers.CharField(read_only=True)  # Hiển thị tên category

    class Meta:
        model = Task
        fields = [
            'task_id', 'task_name', 'description', 'status', 'priority',
            'start_date', 'due_date', 'actual_end_date', 'assignee', 'assignee_id',
            'project', 'category', 'category_name', 'progress',
            'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'task_id': {'required': False},
            'progress': {'required': False},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
            'project': {'write_only': True},
            'category': {'write_only': True}
        }

    def create(self, validated_data):
        # Xử lý assignee
        assignee_id = validated_data.pop('assignee_id', None)
        assignee = None
        if assignee_id:
            try:
                assignee = User.objects.get(user_id=assignee_id)
            except User.DoesNotExist:
                raise serializers.ValidationError({'assignee_id': 'Assignee không tồn tại'})

        # Xử lý project
        project_id = validated_data.get('project')
        if project_id:
            try:
                project = Project.objects.get(project_id=project_id)
                validated_data['project'] = project
            except Project.DoesNotExist:
                raise serializers.ValidationError({'project': 'Project không tồn tại'})

        # Xử lý category
        category_id = validated_data.get('category')
        if category_id:
            try:
                category = TaskCategory.objects.get(id=category_id)
                validated_data['category'] = category
                validated_data['category_name'] = category.name
            except TaskCategory.DoesNotExist:
                raise serializers.ValidationError({'category': 'Category không tồn tại'})

        # Tạo task
        task = Task(assignee=assignee, **validated_data)
        task.save()
        return task

    def update(self, instance, validated_data):
        # Xử lý assignee
        assignee_id = validated_data.pop('assignee_id', None)
        if assignee_id:
            try:
                instance.assignee = User.objects.get(user_id=assignee_id)
            except User.DoesNotExist:
                raise serializers.ValidationError({'assignee_id': 'Assignee không tồn tại'})

        # Xử lý category
        category_id = validated_data.get('category')
        if category_id:
            try:
                category = TaskCategory.objects.get(id=category_id)
                instance.category = category
                instance.category_name = category.name
            except TaskCategory.DoesNotExist:
                raise serializers.ValidationError({'category': 'Category không tồn tại'})

        # Cập nhật các field còn lại
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
