# api/serializers/task_serializer.py
from datetime import timezone
from rest_framework import serializers
from api.models.task import Task
from api.models.user import User
from api.models.project import Project
from api.models.task_category import TaskCategory
from api.serializers.user_serializer import UserSerializer

class TaskCategorySimpleSerializer(serializers.ModelSerializer):
    """Simple serializer cho TaskCategory (tránh circular import)"""
    class Meta:
        model = TaskCategory
        fields = ['id', 'name', 'project_id']

class ProjectSimpleSerializer(serializers.ModelSerializer):
    """Simple serializer cho Project"""
    class Meta:
        model = Project
        fields = ['project_id', 'project_name']

class TaskSerializer(serializers.ModelSerializer):
    # Read-only fields (cho output)
    assignee = UserSerializer(read_only=True)
    category_info = TaskCategorySimpleSerializer(source='category', read_only=True)
    project_info = ProjectSimpleSerializer(source='project', read_only=True)
    
    # Write-only fields (cho input)
    assignee_id = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    project_id = serializers.CharField(write_only=True, required=True)
    category_id = serializers.CharField(write_only=True, required=True)
    
    # Backward compatibility với response cũ
    category_name = serializers.ReadOnlyField(source='category.name')
    
    class Meta:
        model = Task
        fields = [
            # Read fields
            'task_id', 'task_name', 'description', 'status', 'priority',
            'start_date', 'due_date', 'actual_end_date', 'progress',
            'created_at', 'updated_at',
            
            # Relationship fields (read-only)
            'assignee', 'category_info', 'project_info', 'category_name',
            
            # Input fields (write-only)
            'assignee_id', 'project_id', 'category_id'
        ]
        extra_kwargs = {
            'task_id': {'required': False, 'read_only': True},
            'progress': {'required': False, 'default': 0},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }
    
    def validate_assignee_id(self, value):
        """Validate assignee exists"""
        if value and value.strip():
            try:
                User.objects.get(user_id=value)
            except User.DoesNotExist:
                raise serializers.ValidationError(f"User with id '{value}' does not exist")
        return value
    
    def validate_project_id(self, value):
        """Validate project exists"""
        try:
            Project.objects.get(project_id=value)
        except Project.DoesNotExist:
            raise serializers.ValidationError(f"Project with id '{value}' does not exist")
        return value
    
    def validate_category_id(self, value):
        """Validate category exists"""
        try:
            TaskCategory.objects.get(id=value)
        except TaskCategory.DoesNotExist:
            raise serializers.ValidationError(f"Category with id '{value}' does not exist")
        return value
    
    def validate(self, attrs):
        """Cross-field validation"""
        # Ensure category belongs to the project
        if 'category_id' in attrs and 'project_id' in attrs:
            try:
                category = TaskCategory.objects.get(id=attrs['category_id'])
                project = Project.objects.get(project_id=attrs['project_id'])
                
                if category.project_id != project.project_id:
                    raise serializers.ValidationError({
                        'category_id': 'Category must belong to the specified project'
                    })
            except (TaskCategory.DoesNotExist, Project.DoesNotExist):
                pass  # Will be caught by individual field validators
        
        # Validate dates
        if 'start_date' in attrs and 'due_date' in attrs:
            if attrs['start_date'] and attrs['due_date']:
                if attrs['start_date'] > attrs['due_date']:
                    raise serializers.ValidationError({
                        'due_date': 'Due date must be after start date'
                    })
        
        return attrs
    
    def create(self, validated_data):
        assignee_id = validated_data.pop('assignee_id', None)
        project_id = validated_data.pop('project_id')
        category_id = validated_data.pop('category_id')
        
        print(f"Assignee ID: {assignee_id}, Project ID: {project_id}, Category ID: {category_id}")
        
        assignee = None
        if assignee_id and assignee_id.strip():
            try:
                assignee = User.objects.get(user_id=assignee_id)
            except User.DoesNotExist:
                print(f"User with ID '{assignee_id}' does not exist")
                raise serializers.ValidationError(f"User with ID '{assignee_id}' does not exist")
        
        try:
            project = Project.objects.get(project_id=project_id)
        except Project.DoesNotExist:
            print(f"Project with ID '{project_id}' does not exist")
            raise serializers.ValidationError(f"Project with ID '{project_id}' does not exist")
        
        try:
            category = TaskCategory.objects.get(id=category_id)
        except TaskCategory.DoesNotExist:
            print(f"Category with ID '{category_id}' does not exist")
            raise serializers.ValidationError(f"Category with ID '{category_id}' does not exist")
        
        # Create task
        task = Task.objects.create(
            assignee=assignee,
            project=project,
            category=category,
            **validated_data
        )
        
        return task
    
    def update(self, instance, validated_data):
        # Handle assignee update
        if 'assignee_id' in validated_data:
            assignee_id = validated_data.pop('assignee_id')
            if assignee_id and assignee_id.strip():
                instance.assignee = User.objects.get(user_id=assignee_id)
            else:
                instance.assignee = None
        
        # Handle project update
        if 'project_id' in validated_data:
            project_id = validated_data.pop('project_id')
            instance.project = Project.objects.get(project_id=project_id)
        
        # Handle category update
        if 'category_id' in validated_data:
            category_id = validated_data.pop('category_id')
            instance.category = TaskCategory.objects.get(id=category_id)
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Auto-update status based on progress
        if instance.progress == 100 and instance.status != 'Done':
            instance.status = 'Done'
        elif instance.progress < 100 and instance.status == 'Done':
            instance.status = 'In Progress'
        
        instance.save()
        return instance
    
    def to_representation(self, instance):
        """Customize the output representation"""
        data = super().to_representation(instance)
        
        # Add computed fields
        data['is_overdue'] = instance.is_overdue() if hasattr(instance, 'is_overdue') else False
        data['days_remaining'] = instance.days_remaining() if hasattr(instance, 'days_remaining') else None
        
        # Format dates for frontend
        if data.get('start_date'):
            data['start_date_formatted'] = instance.start_date.strftime('%Y-%m-%d')
        if data.get('due_date'):
            data['due_date_formatted'] = instance.due_date.strftime('%Y-%m-%d')
            
        return data


class UserTasksSerializer(serializers.Serializer):
    """Serializer để lấy tasks của user cụ thể"""
    user_id = serializers.CharField(required=True)
    include_completed = serializers.BooleanField(default=False)
    project_id = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(required=False, allow_blank=True)
    priority = serializers.CharField(required=False, allow_blank=True)
    
    def validate_user_id(self, value):
        """Validate user exists"""
        try:
            User.objects.get(user_id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User with id '{value}' does not exist")
        return value
    
    def validate_project_id(self, value):
        """Validate project exists if provided"""
        if value and value.strip():
            try:
                Project.objects.get(project_id=value)
            except Project.DoesNotExist:
                raise serializers.ValidationError(f"Project with id '{value}' does not exist")
        return value
    
    def get_user_tasks(self):
        """Lấy tasks của user theo các filter được chỉ định"""
        validated_data = self.validated_data
        user_id = validated_data['user_id']
        
        # Base queryset
        queryset = Task.objects.filter(assignee__user_id=user_id)
        
        # Filter theo completion status
        if not validated_data.get('include_completed', False):
            queryset = queryset.exclude(status='Done')
        
        # Filter theo project
        if validated_data.get('project_id'):
            queryset = queryset.filter(project__project_id=validated_data['project_id'])
        
        # Filter theo status
        if validated_data.get('status'):
            queryset = queryset.filter(status=validated_data['status'])
        
        # Filter theo priority
        if validated_data.get('priority'):
            queryset = queryset.filter(priority=validated_data['priority'])
        
        # Order by due_date và priority
        queryset = queryset.select_related('assignee', 'project', 'category').order_by('due_date', '-priority')
        
        return queryset


# Helper functions để sử dụng trong views
def get_user_tasks(user_id, **filters):
    """
    Helper function để lấy tasks của user
    
    Args:
        user_id: ID của user
        **filters: Các filter khác như project_id, status, priority, include_completed
    
    Returns:
        QuerySet của Task objects
    """
    data = {'user_id': user_id, **filters}
    serializer = UserTasksSerializer(data=data)
    
    if serializer.is_valid():
        return serializer.get_user_tasks()
    else:
        raise ValueError(f"Invalid parameters: {serializer.errors}")


def get_user_task_summary(user_id):
    """
    Lấy summary về tasks của user
    
    Returns:
        Dict với thông tin tổng quan về tasks
    """
    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        raise ValueError(f"User with id '{user_id}' does not exist")
    
    tasks = Task.objects.filter(assignee=user)
    
    summary = {
        'user_id': user_id,
        'user_name': f"{user.first_name} {user.last_name}".strip(),
        'total_tasks': tasks.count(),
        'completed_tasks': tasks.filter(status='Done').count(),
        'in_progress_tasks': tasks.filter(status='In Progress').count(),
        'pending_tasks': tasks.filter(status='Pending').count(),
        'overdue_tasks': tasks.filter(
            due_date__lt=timezone.now().date(),
            status__in=['Pending', 'In Progress']
        ).count() if hasattr(tasks.first(), 'due_date') else 0,
        'high_priority_tasks': tasks.filter(priority='High', status__in=['Pending', 'In Progress']).count(),
    }
    
    return summary