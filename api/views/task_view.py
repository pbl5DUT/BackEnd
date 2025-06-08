# api/views/task_view.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone

from api.models.task import Task
from api.models.task_comment import TaskComment
from api.models.task_attachment import TaskAttachment
from api.models.user import User
from api.models.project import Project

from api.serializers.task_serializer import TaskSerializer, UserTasksSerializer
from api.serializers.task_comment_serializer import TaskCommentSerializer
from api.serializers.task_attachment_serializer import TaskAttachmentSerializer


# Helper functions để lấy tasks theo user
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
        ).count(),
        'high_priority_tasks': tasks.filter(priority='High', status__in=['Pending', 'In Progress']).count(),
    }
    
    return summary


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    lookup_field = 'task_id'
    permission_classes = []
    
    # Filtering và search
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'assignee__user_id', 'project__project_id', 'category__id']
    search_fields = ['task_name', 'description']
    ordering_fields = ['created_at', 'due_date', 'priority', 'status', 'progress']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Task.objects.all()
        
        # Lọc theo URL parameters từ nested routes
        project_pk = self.kwargs.get('project_pk')
        category_pk = self.kwargs.get('category_pk')
        
        if project_pk:
            queryset = queryset.filter(project__project_id=project_pk)
            print(f"Filtered by project_pk from URL: {project_pk}")
            
        if category_pk:
            queryset = queryset.filter(category__id=category_pk)
            print(f"Filtered by category_pk from URL: {category_pk}")
        
        # Các logic lọc hiện tại
        # Lọc theo project_id
        project_id = self.request.query_params.get('project_id')
        if project_id and not project_pk:
            queryset = queryset.filter(project__project_id=project_id)
            
        # Lọc theo assignee_id
        assignee_id = self.request.query_params.get('assignee_id')
        if assignee_id:
            queryset = queryset.filter(assignee__user_id=assignee_id)
            
        # Lọc theo status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
            
        # Lọc theo priority
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
            
        # Lọc theo category_id
        category_id = self.request.query_params.get('category_id')
        if category_id and not category_pk:
            queryset = queryset.filter(category__id=category_id)
            
        # Tìm kiếm theo từ khóa
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(task_name__icontains=search) | 
                Q(description__icontains=search)
            )
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        print(f"Create task called with kwargs: {kwargs}")
        
        # Lấy project_id và category_id từ URL 
        project_pk = self.kwargs.get('project_pk')
        category_pk = self.kwargs.get('category_pk')
        
        # Tạo bản sao của request.data
        data = request.data.copy()
        
        # Thêm project_id và category_id từ URL vào data nếu có
        if project_pk:
            data['project_id'] = project_pk
            print(f"Added project_id from URL: {project_pk}")
            
        if category_pk:
            data['category_id'] = category_pk
            print(f"Added category_id from URL: {category_pk}")
        
        # Tiếp tục với quá trình tạo task
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    # ===============================
    # ORIGINAL ACTIONS (HIỆN TẠI)
    # ===============================
    
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
    
    # ===============================
    # NEW USER TASK ACTIONS
    # ===============================
    
    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)')
    def get_user_tasks(self, request, user_id=None):
        """
        API endpoint để lấy tất cả tasks của user cụ thể
        
        URL: /api/tasks/user/{user_id}/
        
        Query parameters:
        - include_completed: boolean (default: false) - Bao gồm cả task đã hoàn thành
        - project_id: string - Filter theo project
        - status: string - Filter theo status
        - priority: string - Filter theo priority
        """
        try:
            # Lấy parameters từ query string
            params = {
                'user_id': user_id,
                'include_completed': request.query_params.get('include_completed', 'true').lower() == 'true',
                'project_id': request.query_params.get('project_id', ''),
                'status': request.query_params.get('status', ''),
                'priority': request.query_params.get('priority', ''),
            }
            
            # Sử dụng helper function
            tasks = get_user_tasks(**params)
            
            # Serialize tasks
            serializer = TaskSerializer(tasks, many=True)
            
            return Response({
                'success': True,
                'data': {
                    'user_id': user_id,
                    'tasks': serializer.data,
                    'total_count': tasks.count(),
                    'filters_applied': {k: v for k, v in params.items() if v and k != 'user_id'}
                }
            })
            
        except ValueError as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)/summary')
    def get_user_task_summary(self, request, user_id=None):
        """
        API endpoint để lấy summary về tasks của user
        
        URL: /api/tasks/user/{user_id}/summary/
        """
        try:
            summary = get_user_task_summary(user_id)
            
            return Response({
                'success': True,
                'data': summary
            })
            
        except ValueError as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], url_path='user/filter')
    def filter_user_tasks(self, request):
        """
        API endpoint để lấy tasks của user với filter phức tạp
        
        URL: /api/tasks/user/filter/
        Method: POST
        
        Body:
        {
            "user_id": "string",
            "include_completed": boolean,
            "project_id": "string",
            "status": "string", 
            "priority": "string"
        }
        """
        serializer = UserTasksSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                tasks = serializer.get_user_tasks()
                task_serializer = TaskSerializer(tasks, many=True)
                
                return Response({
                    'success': True,
                    'data': {
                        'tasks': task_serializer.data,
                        'total_count': tasks.count(),
                        'filters_applied': serializer.validated_data
                    }
                })
                
            except Exception as e:
                return Response({
                    'success': False,
                    'error': 'Internal server error'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)/pending')
    def get_user_pending_tasks(self, request, user_id=None):
        """
        API endpoint để lấy tất cả pending tasks của user
        
        URL: /api/tasks/user/{user_id}/pending/
        """
        try:
            tasks = get_user_tasks(user_id=user_id, status='Pending')
            serializer = TaskSerializer(tasks, many=True)
            
            return Response({
                'success': True,
                'data': {
                    'user_id': user_id,
                    'pending_tasks': serializer.data,
                    'count': tasks.count()
                }
            })
            
        except ValueError as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)/overdue')
    def get_user_overdue_tasks(self, request, user_id=None):
        """
        API endpoint để lấy tất cả overdue tasks của user
        
        URL: /api/tasks/user/{user_id}/overdue/
        """
        try:
            # Lấy tasks của user chưa hoàn thành
            tasks = get_user_tasks(user_id=user_id, include_completed=False)
            
            # Filter chỉ lấy tasks overdue
            overdue_tasks = tasks.filter(
                due_date__lt=timezone.now().date()
            )
            
            serializer = TaskSerializer(overdue_tasks, many=True)
            
            return Response({
                'success': True,
                'data': {
                    'user_id': user_id,
                    'overdue_tasks': serializer.data,
                    'count': overdue_tasks.count()
                }
            })
            
        except ValueError as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)/project/(?P<project_id>[^/.]+)')
    def get_user_tasks_by_project(self, request, user_id=None, project_id=None):
        """
        API endpoint để lấy tasks của user trong project cụ thể
        
        URL: /api/tasks/user/{user_id}/project/{project_id}/
        """
        try:
            tasks = get_user_tasks(
                user_id=user_id, 
                project_id=project_id,
                include_completed=request.query_params.get('include_completed', 'false').lower() == 'true'
            )
            
            serializer = TaskSerializer(tasks, many=True)
            
            return Response({
                'success': True,
                'data': {
                    'user_id': user_id,
                    'project_id': project_id,
                    'tasks': serializer.data,
                    'count': tasks.count()
                }
            })
            
        except ValueError as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)/high-priority')
    def get_user_high_priority_tasks(self, request, user_id=None):
        """
        API endpoint để lấy tất cả high priority tasks của user
        
        URL: /api/tasks/user/{user_id}/high-priority/
        """
        try:
            tasks = get_user_tasks(user_id=user_id, priority='High', include_completed=False)
            serializer = TaskSerializer(tasks, many=True)
            
            return Response({
                'success': True,
                'data': {
                    'user_id': user_id,
                    'high_priority_tasks': serializer.data,
                    'count': tasks.count()
                }
            })
            
        except ValueError as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)/recent')
    def get_user_recent_tasks(self, request, user_id=None):
        """
        API endpoint để lấy tasks gần đây của user (7 ngày gần nhất)
        
        URL: /api/tasks/user/{user_id}/recent/
        """
        try:
            # Lấy tasks được tạo trong 7 ngày gần nhất
            seven_days_ago = timezone.now() - timezone.timedelta(days=7)
            tasks = get_user_tasks(user_id=user_id, include_completed=True)
            recent_tasks = tasks.filter(created_at__gte=seven_days_ago)
            
            serializer = TaskSerializer(recent_tasks, many=True)
            
            return Response({
                'success': True,
                'data': {
                    'user_id': user_id,
                    'recent_tasks': serializer.data,
                    'count': recent_tasks.count(),
                    'period': '7 days'
                }
            })
            
        except ValueError as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)