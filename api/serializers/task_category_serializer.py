# api/serializers/task_category_serializer.py

from rest_framework import serializers
from api.models.task_category import TaskCategory
from api.models.project import Project

class TaskCategorySerializer(serializers.ModelSerializer):
    # Sử dụng project_id làm giá trị đại diện khi tạo category
    project = serializers.SlugRelatedField(
        queryset=Project.objects.all(),
        slug_field='project_id'
    )

    class Meta:
        model = TaskCategory
        fields = [
            'id',
            'name',
            'description',
            'project',
            'tasks_count',
            'completed_tasks_count',
            'created_at',
            'updated_at'
        ]
        extra_kwargs = {
            'id': {'required': False},
            'tasks_count': {'read_only': True},
            'completed_tasks_count': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }
