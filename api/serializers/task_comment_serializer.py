# api/serializers/task_comment_serializer.py
from rest_framework import serializers
from api.models.task_comment import TaskComment
from api.models.task import Task
from api.models.user import User
from api.serializers.user_serializer import UserSerializer

class TaskCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.CharField(write_only=True, required=False)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = TaskComment
        fields = [
            'id', 'content', 'created_at', 'task', 'user', 'user_id',
            'parent_comment', 'replies'
        ]
        extra_kwargs = {
            'id': {'required': False},
            'created_at': {'read_only': True},
            'task': {'write_only': True},
            'parent_comment': {'write_only': True}
        }
    
    def get_replies(self, obj):
        # Lấy các reply cho comment này
        replies = TaskComment.objects.filter(parent_comment=obj)
        return TaskCommentSerializer(replies, many=True).data
    
    def create(self, validated_data):
        # Xử lý user_id
        user_id = validated_data.pop('user_id', None) or self.context.get('request').user.user_id
        
        if user_id:
            try:
                user = User.objects.get(user_id=user_id)
            except User.DoesNotExist:
                raise serializers.ValidationError({'user_id': 'User không tồn tại'})
        else:
            raise serializers.ValidationError({'user_id': 'User ID không được cung cấp'})
            
        # Kiểm tra task
        task_id = validated_data.get('task')
        if task_id:
            try:
                task = Task.objects.get(task_id=task_id)
                validated_data['task'] = task
            except Task.DoesNotExist:
                raise serializers.ValidationError({'task': 'Task không tồn tại'})
        
        # Kiểm tra parent_comment nếu có
        parent_id = validated_data.get('parent_comment')
        if parent_id:
            try:
                parent = TaskComment.objects.get(id=parent_id)
                validated_data['parent_comment'] = parent
            except TaskComment.DoesNotExist:
                raise serializers.ValidationError({'parent_comment': 'Parent comment không tồn tại'})
        
        # Tạo comment
        comment = TaskComment(user=user, **validated_data)
        comment.save()
        
        return comment