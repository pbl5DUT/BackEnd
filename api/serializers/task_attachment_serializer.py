# api/serializers/task_attachment_serializer.py
from rest_framework import serializers
from api.models.task_attachment import TaskAttachment
from api.models.task import Task
from api.models.user import User
from api.serializers.user_serializer import UserSerializer

class TaskAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    uploaded_by_id = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = TaskAttachment
        fields = [
            'id', 'name', 'file_url', 'file_type', 'file_size',
            'uploaded_at', 'uploaded_by', 'uploaded_by_id', 'task'
        ]
        extra_kwargs = {
            'id': {'required': False},
            'uploaded_at': {'read_only': True},
            'task': {'write_only': True}
        }
    
    def create(self, validated_data):
        # Xử lý uploaded_by_id
        uploaded_by_id = validated_data.pop('uploaded_by_id', None) or self.context.get('request').user.user_id
        
        if uploaded_by_id:
            try:
                uploaded_by = User.objects.get(user_id=uploaded_by_id)
            except User.DoesNotExist:
                raise serializers.ValidationError({'uploaded_by_id': 'User không tồn tại'})
        else:
            raise serializers.ValidationError({'uploaded_by_id': 'User ID không được cung cấp'})
            
        # Kiểm tra task
        task_id = validated_data.get('task')
        if task_id:
            try:
                task = Task.objects.get(task_id=task_id)
                validated_data['task'] = task
            except Task.DoesNotExist:
                raise serializers.ValidationError({'task': 'Task không tồn tại'})
        
        # Tạo attachment
        attachment = TaskAttachment(uploaded_by=uploaded_by, **validated_data)
        attachment.save()
        
        return attachment