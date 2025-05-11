# api/views/task_category_view.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from api.models.task_category import TaskCategory
from api.models.task import Task
from api.serializers.task_category_serializer import TaskCategorySerializer
from api.serializers.task_serializer import TaskSerializer

class TaskCategoryViewSet(viewsets.ModelViewSet):
    queryset = TaskCategory.objects.all()
    serializer_class = TaskCategorySerializer
    lookup_field = 'id'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'tasks_count', 'completed_tasks_count']
    
    def get_queryset(self):
        queryset = TaskCategory.objects.all()
        
        # Lấy project_id từ parameter đúng
        project_id = self.kwargs.get('project_project_id')  # Đây là tên parameter đúng
        print(f"🔍 project_project_id from URL: {project_id}")
        
        if project_id:
            queryset = queryset.filter(project__project_id=project_id)
            print(f"🔍 Filtered queryset count: {queryset.count()}")
        
        return queryset

    @action(detail=True, methods=['get'])
    def tasks(self, request, id=None):
        """
        Lấy danh sách task của category
        URL: GET /api/categories/{id}/tasks/
        """
        category = self.get_object()
        tasks = Task.objects.filter(category=category)
        
        # Lọc theo status nếu có
        status_param = request.query_params.get('status')
        if status_param:
            tasks = tasks.filter(status=status_param)
            
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Lấy thống kê theo category
        URL: GET /api/categories/stats/
        """
        project_id = request.query_params.get('project_id')
        if not project_id:
            return Response(
                {"error": "project_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        categories = TaskCategory.objects.filter(project__project_id=project_id)
        
        result = []
        for category in categories:
            # Lấy số lượng task theo từng trạng thái
            todo_count = Task.objects.filter(category=category, status='Todo').count()
            in_progress_count = Task.objects.filter(category=category, status='In Progress').count()
            review_count = Task.objects.filter(category=category, status='Review').count()
            done_count = Task.objects.filter(category=category, status='Done').count()
            
            result.append({
                'id': category.id,
                'name': category.name,
                'tasks_count': category.tasks_count,
                'completed_tasks_count': category.completed_tasks_count,
                'stats': {
                    'todo': todo_count,
                    'in_progress': in_progress_count,
                    'review': review_count,
                    'done': done_count
                }
            })
            
        return Response(result)