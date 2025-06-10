# api/views.py
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from django.utils import timezone
from django.db import transaction

from api.models.work_report import WorkReport
from api.serializers.work_report_serializers import (
    WorkReportSerializer,
    WorkReportListSerializer,
    WorkReportDetailSerializer
)


class WorkReportViewSet(viewsets.ModelViewSet):
    queryset = WorkReport.objects.all()
    
    def get_serializer_class(self):
        """
        Sử dụng serializer khác nhau dựa trên action
        """
        if self.action == 'list':
            return WorkReportListSerializer
        elif self.action == 'retrieve':
            return WorkReportDetailSerializer
        return WorkReportSerializer
    
    def get_queryset(self):
        """
        ✅ FIX: Sửa lỗi prefetch_related với project members
        """
        queryset = WorkReport.objects.select_related(
            'user', 
            'project'
            # ✅ REMOVED: 'project__manager' vì có thể không có field này
        ).prefetch_related(
            'tasks'
            # ✅ REMOVED: 'project__members', 'project__members__user' 
            # vì Project không có field members trực tiếp
            # Nếu cần thì dùng: 'project__projectuser_set', 'project__projectuser_set__user'
        )
        
        # ✅ Thêm filter parameters cho list view
        if self.action == 'list':
            user_id = self.request.query_params.get('user_id')
            project_id = self.request.query_params.get('project_id')
            status_filter = self.request.query_params.get('status')
            type_filter = self.request.query_params.get('type')  # ✅ Thêm filter theo type
            
            if user_id:
                queryset = queryset.filter(user__user_id=user_id)
            if project_id:
                queryset = queryset.filter(project__project_id=project_id)
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            if type_filter:
                queryset = queryset.filter(type=type_filter)
        
        return queryset.order_by('-created_at')

    def create(self, request, *args, **kwargs):
        """
        Override create để thêm validation và error handling
        """
        try:
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                
                # Sử dụng DetailSerializer để trả về response đầy đủ
                detail_serializer = WorkReportDetailSerializer(
                    serializer.instance, 
                    context=self.get_serializer_context()
                )
                headers = self.get_success_headers(detail_serializer.data)
                return Response(
                    detail_serializer.data, 
                    status=status.HTTP_201_CREATED, 
                    headers=headers
                )
        except Exception as e:
            return Response(
                {'error': f'Có lỗi xảy ra khi tạo work report: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        """
        Override update để thêm validation
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Kiểm tra trạng thái có thể edit
        if instance.status == 'REVIEWED':
            return Response(
                {'error': 'Không thể chỉnh sửa work report đã được review'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                serializer = self.get_serializer(instance, data=request.data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)

                # Sử dụng DetailSerializer để trả về response đầy đủ
                detail_serializer = WorkReportDetailSerializer(
                    serializer.instance, 
                    context=self.get_serializer_context()
                )
                return Response(detail_serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Có lỗi xảy ra khi cập nhật work report: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    # Thêm hành động submit để thay đổi trạng thái báo cáo
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """
        Submit work report - chuyển từ DRAFT sang SUBMITTED
        """
        try:
            with transaction.atomic():
                workreport = self.get_object()
                
                # Kiểm tra nếu báo cáo chưa được nộp
                if workreport.status != 'DRAFT':
                    return Response(
                        {'error': 'Work report không ở trạng thái DRAFT'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Validation bổ sung - kiểm tra có tasks không
                if not workreport.tasks.exists():
                    return Response(
                        {'error': 'Work report phải có ít nhất 1 task trước khi submit'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Thay đổi trạng thái báo cáo thành 'SUBMITTED'
                workreport.status = 'SUBMITTED'
                workreport.submitted_date = timezone.now()
                workreport.save()

                # Trả về thông tin đầy đủ sau khi submit
                detail_serializer = WorkReportDetailSerializer(
                    workreport, 
                    context=self.get_serializer_context()
                )
                
                return Response({
                    'message': 'Work report đã được submit thành công',
                    'data': detail_serializer.data
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response(
                {'error': f'Có lỗi xảy ra khi submit work report: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # Thêm hành động review để thay đổi trạng thái báo cáo thành 'REVIEWED'
    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        """
        Review work report - chuyển từ SUBMITTED sang REVIEWED
        """
        try:
            with transaction.atomic():
                workreport = self.get_object()

                # Kiểm tra nếu báo cáo không phải là 'SUBMITTED'
                if workreport.status != 'SUBMITTED':
                    return Response(
                        {'error': 'Work report chưa được submit hoặc đã được review'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Lấy thông tin reviewer
                reviewer_info = getattr(request.user, 'username', None)
                if not reviewer_info:
                    reviewer_info = getattr(request.user, 'user_id', 'Unknown')

                # Cập nhật trạng thái báo cáo thành 'REVIEWED'
                workreport.status = 'REVIEWED'
                workreport.reviewed_date = timezone.now()
                workreport.reviewed_by = reviewer_info
                
                # Có thể thêm review comment nếu có
                review_comment = request.data.get('review_comment', '')
                if review_comment and hasattr(workreport, 'review_comment'):
                    workreport.review_comment = review_comment
                
                workreport.save()

                # Trả về thông tin đầy đủ sau khi review
                detail_serializer = WorkReportDetailSerializer(
                    workreport, 
                    context=self.get_serializer_context()
                )

                return Response({
                    'message': 'Work report đã được review thành công',
                    'data': detail_serializer.data
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response(
                {'error': f'Có lỗi xảy ra khi review work report: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """
        Reject work report - chuyển từ SUBMITTED về DRAFT
        """
        try:
            with transaction.atomic():
                workreport = self.get_object()

                # Kiểm tra nếu báo cáo không phải là 'SUBMITTED'
                if workreport.status != 'SUBMITTED':
                    return Response(
                        {'error': 'Chỉ có thể reject work report ở trạng thái SUBMITTED'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Lấy lý do reject
                reject_reason = request.data.get('reject_reason', '')
                if not reject_reason:
                    return Response(
                        {'error': 'Vui lòng cung cấp lý do reject'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Cập nhật trạng thái về DRAFT
                workreport.status = 'DRAFT'
                
                # ✅ Chỉ set reject fields nếu model có
                if hasattr(workreport, 'reject_reason'):
                    workreport.reject_reason = reject_reason
                if hasattr(workreport, 'rejected_date'):
                    workreport.rejected_date = timezone.now()
                if hasattr(workreport, 'rejected_by'):
                    workreport.rejected_by = getattr(request.user, 'username', 'Unknown')
                
                # Reset submitted_date
                workreport.submitted_date = None
                workreport.save()

                # Trả về thông tin đầy đủ sau khi reject
                detail_serializer = WorkReportDetailSerializer(
                    workreport, 
                    context=self.get_serializer_context()
                )

                return Response({
                    'message': 'Work report đã được reject',
                    'data': detail_serializer.data
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response(
                {'error': f'Có lỗi xảy ra khi reject work report: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def my_reports(self, request):
        """
        Lấy danh sách work reports của user hiện tại
        """
        try:
            user_id = getattr(request.user, 'user_id', None)
            if not user_id:
                return Response(
                    {'error': 'Không thể xác định user_id'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            queryset = self.get_queryset().filter(user__user_id=user_id)
            page = self.paginate_queryset(queryset)
            
            if page is not None:
                serializer = WorkReportListSerializer(page, many=True, context=self.get_serializer_context())
                return self.get_paginated_response(serializer.data)

            serializer = WorkReportListSerializer(queryset, many=True, context=self.get_serializer_context())
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': f'Có lỗi xảy ra: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Thống kê work reports theo trạng thái
        """
        try:
            from django.db.models import Count
            
            queryset = self.get_queryset()
            
            # Filter theo user nếu có
            user_id = request.query_params.get('user_id')
            if user_id:
                queryset = queryset.filter(user__user_id=user_id)
            
            # Filter theo project nếu có
            project_id = request.query_params.get('project_id')
            if project_id:
                queryset = queryset.filter(project__project_id=project_id)

            # Thống kê theo status
            status_stats = queryset.values('status').annotate(count=Count('status')).order_by('status')
            
            # ✅ Thêm thống kê theo type
            type_stats = queryset.values('type').annotate(count=Count('type')).order_by('type')
            
            total = queryset.count()
            
            return Response({
                'total_reports': total,
                'status_breakdown': list(status_stats),
                'type_breakdown': list(type_stats),  # ✅ Thêm type breakdown
                'summary': {
                    'draft': queryset.filter(status='DRAFT').count(),
                    'submitted': queryset.filter(status='SUBMITTED').count(),
                    'reviewed': queryset.filter(status='REVIEWED').count(),
                },
                'type_summary': {  # ✅ Thêm type summary
                    'daily': queryset.filter(type='DAILY').count(),
                    'weekly': queryset.filter(type='WEEKLY').count(),
                    'monthly': queryset.filter(type='MONTHLY').count(),
                }
            })
            
        except Exception as e:
            return Response(
                {'error': f'Có lỗi xảy ra khi thống kê: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # ✅ THÊM: User tasks for reporting endpoint
    @action(detail=False, methods=['get'])
    def user_tasks_for_reporting(self, request):
        """
        Lấy danh sách tasks của user trong khoảng thời gian để tạo báo cáo
        GET /api/work-reports/user_tasks_for_reporting/?user_id=xxx&start_date=2025-06-10&end_date=2025-06-16
        """
        try:
            user_id = request.query_params.get('user_id')
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            project_id = request.query_params.get('project_id')  # Optional
            
            if not all([user_id, start_date, end_date]):
                return Response(
                    {'error': 'user_id, start_date, end_date là bắt buộc'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                from api.models.task import Task
                from django.db.models import Q
                
                # Filter tasks của user trong khoảng thời gian
                queryset = Task.objects.filter(
                    assigned_to__user_id=user_id,
                    updated_at__date__gte=start_date,
                    updated_at__date__lte=end_date
                ).select_related('project', 'assigned_to')
                
                if project_id:
                    queryset = queryset.filter(project__project_id=project_id)
                
                # Serialize tasks
                tasks_data = []
                for task in queryset:
                    tasks_data.append({
                        'task_id': task.task_id,
                        'task_name': getattr(task, 'task_name', ''),
                        'description': getattr(task, 'description', ''),
                        'status': getattr(task, 'status', ''),
                        'priority': getattr(task, 'priority', ''),
                        'start_date': getattr(task, 'start_date', ''),
                        'due_date': getattr(task, 'due_date', ''),
                        'progress': getattr(task, 'progress', 0),
                        'time_spent': getattr(task, 'time_spent', 0),
                        'updated_at': task.updated_at,
                        'project': {
                            'project_id': task.project.project_id,
                            'project_name': task.project.project_name,
                        } if task.project else None
                    })
                
                return Response({
                    'count': len(tasks_data),
                    'user_id': user_id,
                    'date_range': f"{start_date} to {end_date}",
                    'results': tasks_data
                })
                
            except ImportError:
                # Nếu không có Task model
                return Response({
                    'count': 0,
                    'user_id': user_id,
                    'date_range': f"{start_date} to {end_date}",
                    'results': [],
                    'message': 'Task model not available'
                })
                
        except Exception as e:
            return Response(
                {'error': f'Có lỗi xảy ra: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # ✅ THÊM: Tasks management endpoints
    @action(detail=True, methods=['get', 'post', 'delete'])
    def tasks(self, request, pk=None):
        """
        Quản lý tasks của work report
        GET: Lấy danh sách tasks
        POST: Thêm task vào work report
        DELETE: Xóa task khỏi work report
        """
        if request.method == 'GET':
            return self._get_report_tasks(request, pk)
        elif request.method == 'POST':
            return self._add_task_to_report(request, pk)
        elif request.method == 'DELETE':
            return self._remove_task_from_report(request, pk)

    def _get_report_tasks(self, request, report_id):
        """Lấy danh sách tasks của work report"""
        try:
            workreport = self.get_object()
            tasks = workreport.tasks.all()
            
            # Serialize tasks
            tasks_data = []
            for task in tasks:
                tasks_data.append({
                    'task_id': task.task_id,
                    'task_name': getattr(task, 'task_name', ''),
                    'description': getattr(task, 'description', ''),
                    'status': getattr(task, 'status', ''),
                    'priority': getattr(task, 'priority', ''),
                    'progress': getattr(task, 'progress', 0),
                    'time_spent': getattr(task, 'time_spent', 0),
                })
            
            return Response({
                "report_id": workreport.id,
                "report_title": workreport.title,
                "tasks_count": tasks.count(),
                "tasks": tasks_data
            }, status=status.HTTP_200_OK)
            
        except WorkReport.DoesNotExist:
            return Response(
                {"error": f"Work report với ID '{report_id}' không tồn tại"}, 
                status=status.HTTP_404_NOT_FOUND
            )

    def _add_task_to_report(self, request, report_id):
        """Thêm task vào work report"""
        try:
            workreport = self.get_object()
            
            # Kiểm tra có thể edit không
            if workreport.status == 'REVIEWED':
                return Response(
                    {"error": "Không thể thêm task vào work report đã reviewed"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            task_id = request.data.get('task_id')
            if not task_id:
                return Response(
                    {"error": "task_id là bắt buộc"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Kiểm tra task tồn tại
            try:
                from api.models.task import Task
                task = Task.objects.get(task_id=task_id)
            except Task.DoesNotExist:
                return Response(
                    {"error": f"Task với ID '{task_id}' không tồn tại"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            except ImportError:
                return Response(
                    {"error": "Task model not available"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Kiểm tra task đã được thêm chưa
            if workreport.tasks.filter(task_id=task_id).exists():
                return Response(
                    {"error": f"Task '{task_id}' đã có trong work report này"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Thêm task
            workreport.tasks.add(task)
            
            return Response({
                "message": f"Đã thêm task '{task_id}' vào work report",
                "tasks_count": workreport.tasks.count()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Lỗi khi thêm task: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _remove_task_from_report(self, request, report_id):
        """Xóa task khỏi work report"""
        try:
            workreport = self.get_object()
            
            # Kiểm tra có thể edit không
            if workreport.status == 'REVIEWED':
                return Response(
                    {"error": "Không thể xóa task khỏi work report đã reviewed"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            task_id = request.query_params.get('task_id')
            if not task_id:
                return Response(
                    {"error": "task_id parameter là bắt buộc"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Kiểm tra task có trong work report không
            try:
                task = workreport.tasks.get(task_id=task_id)
                workreport.tasks.remove(task)
                
                return Response({
                    "message": f"Đã xóa task '{task_id}' khỏi work report",
                    "tasks_count": workreport.tasks.count()
                }, status=status.HTTP_200_OK)
                
            except:
                return Response(
                    {"error": f"Task '{task_id}' không có trong work report này"},
                    status=status.HTTP_404_NOT_FOUND
                )
                
        except Exception as e:
            return Response(
                {"error": f"Lỗi khi xóa task: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )