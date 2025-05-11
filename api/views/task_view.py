# api/views/task_view.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from api.models.task import Task
from api.models.task_comment import TaskComment
from api.models.task_attachment import TaskAttachment
from api.serializers.task_serializer import TaskSerializer
from api.serializers.task_comment_serializer import TaskCommentSerializer
from api.serializers.task_attachment_serializer import TaskAttachmentSerializer

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    lookup_field = 'task_id'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['task_name', 'description']
    ordering_fields = ['created_at', 'due_date', 'priority', 'status', 'progress']
    
    def get_queryset(self):
        queryset = Task.objects.all()
        
        # Lọc theo project_id
        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(project__project_id=project_id)
            
        # Lọc theo assignee_id
        assignee_id = self.request.query_params.get('assignee_id')
        if assignee_id:
            queryset = queryset.filter(assignee__user_id=assignee_id)
            
        # Lọc theo status
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # Lọc theo priority
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
            
        # Lọc theo category_id
        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(category__id=category_id)
            
        # Tìm kiếm theo từ khóa
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(task_name__icontains=search) | 
                Q(description__icontains=search)
            )
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def comments(self, request, task_id=None):
        """
        Lấy danh sách bình luận của task
        URL: GET /api/tasks/{task_id}/comments/
        """
        task = self.get_object()
        # Chỉ lấy các comment gốc (không có parent)
        comments = TaskComment.objects.filter(task=task, parent_comment=None)
        serializer = TaskCommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, task_id=None):
        """
        Thêm bình luận vào task
        URL: POST /api/tasks/{task_id}/add_comment/
        """
        task = self.get_object()
        
        # Thêm task vào context và data
        data = request.data.copy()
        data['task'] = task.task_id
        
        serializer = TaskCommentSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def attachments(self, request, task_id=None):
        """
        Lấy danh sách tệp đính kèm của task
        URL: GET /api/tasks/{task_id}/attachments/
        """
        task = self.get_object()
        attachments = TaskAttachment.objects.filter(task=task)
        serializer = TaskAttachmentSerializer(attachments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_attachment(self, request, task_id=None):
        """
        Thêm tệp đính kèm vào task
        URL: POST /api/tasks/{task_id}/add_attachment/
        """
        task = self.get_object()
        
        # Thêm task vào context và data
        data = request.data.copy()
        data['task'] = task.task_id
        
        serializer = TaskAttachmentSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, task_id=None):
        """
        Cập nhật trạng thái của task
        URL: PATCH /api/tasks/{task_id}/update_status/
        """
        task = self.get_object()
        status_value = request.data.get('status')
        
        if not status_value:
            return Response(
                {"error": "status field is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Kiểm tra status có hợp lệ không
        if status_value not in dict(Task.STATUS_CHOICES):
            return Response(
                {"error": f"status must be one of {dict(Task.STATUS_CHOICES).keys()}"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Cập nhật status
        task.status = status_value
        
        # Nếu status là Done, cập nhật progress thành 100%
        if status_value == 'Done':
            task.progress = 100
            
        task.save()
        
        serializer = self.get_serializer(task)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def update_progress(self, request, task_id=None):
        """
        Cập nhật tiến độ của task
        URL: PATCH /api/tasks/{task_id}/update_progress/
        """
        task = self.get_object()
        progress = request.data.get('progress')
        
        if progress is None:
            return Response(
                {"error": "progress field is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            progress = int(progress)
        except ValueError:
            return Response(
                {"error": "progress must be an integer"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if progress < 0 or progress > 100:
            return Response(
                {"error": "progress must be between 0 and 100"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Cập nhật progress
        task.progress = progress
        
        # Nếu progress là 100%, cập nhật status thành Done
        if progress == 100 and task.status != 'Done':
            task.status = 'Done'
            
        task.save()
        
        serializer = self.get_serializer(task)
        return Response(serializer.data)