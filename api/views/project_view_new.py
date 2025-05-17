# api/views/project_view.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from api.models.project import Project
from api.models.project_user import ProjectUser
from api.serializers.project_serializer import ProjectSerializer
from api.serializers.project_member_serializer import AddProjectMemberSerializer
from api.serializers.project_user_serializer import ProjectUserSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    lookup_field = 'project_id'  # Sử dụng project_id thay vì pk mặc định
    
    @action(detail=False, methods=['get'])
    def user_projects(self, request):
        """
        Lấy danh sách các dự án mà người dùng hiện tại là thành viên
        URL: GET /api/projects/user-projects/
        """
        user = request.user
        if not user or not user.is_authenticated:
            return Response({"error": "Bạn cần đăng nhập để xem danh sách dự án"}, 
                          status=status.HTTP_401_UNAUTHORIZED)
        
        # Lấy tất cả các dự án mà người dùng hiện tại là thành viên
        project_users = ProjectUser.objects.filter(user=user)
        projects = [pu.project for pu in project_users]
        
        serializer = self.get_serializer(projects, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get', 'post'])
    def members(self, request, project_id=None):
        """
        GET: Lấy danh sách thành viên của dự án
        URL: GET /api/projects/{project_id}/members/
        
        POST: Thêm thành viên vào project
        URL: POST /api/projects/{project_id}/members/
        """
        project = self.get_object()
        
        # Handle GET request
        if request.method == 'GET':
            project_users = ProjectUser.objects.filter(project=project)
            members_data = []
            for pu in project_users:
                user = pu.user
                members_data.append({
                    'id': user.user_id,
                    'name': f"{user.first_name} {user.last_name}".strip() or user.username,
                    'username': user.username,
                    'email': user.email,
                    'avatar': user.avatar.url if user.avatar else None,
                    'role': pu.role_in_project,
                    'isOnline': True  # Placeholder for online status
                })
            return Response(members_data)
        
        # Handle POST request
        try:
            serializer = AddProjectMemberSerializer(data=request.data, context={'project': project})
            
            if serializer.is_valid():
                project_user = serializer.save()
                return Response(
                    ProjectUserSerializer(project_user).data,
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['delete'])
    def remove_member(self, request, project_id=None):
        """
        Xóa thành viên khỏi project
        URL: DELETE /api/projects/{project_id}/members/?user_id={user_id}
        """
        project = self.get_object()
        user_id = request.query_params.get('user_id')
        
        if not user_id:
            return Response(
                {"error": "user_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            project_user = ProjectUser.objects.get(project=project, user__user_id=user_id)
            project_user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProjectUser.DoesNotExist:
            return Response(
                {"error": "User is not a member of this project"},
                status=status.HTTP_404_NOT_FOUND
            )

    # Ghi đè retrieve để có thể trả về dự án với thông tin thành viên
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        # Lấy bản sao của dữ liệu request
        data = request.data.copy()
        
        # Tách members từ dữ liệu request
        members_data = data.pop('members', [])
        
        # Tạo project bằng serializer
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        project = serializer.save()
        
        # Thêm debug để theo dõi quá trình
        print(f"Project đã được tạo: {project.project_id}")
        print(f"Thành viên cần thêm: {members_data}")
        
        # Thêm các thành viên vào project
        for member_data in members_data:
            try:
                # Map vai trò nếu cần - ví dụ: Developer -> Member
                role_mapping = {
                    'Developer': 'Member',
                    'Tester': 'Support'
                }
                
                original_role = member_data.get('role_in_project')
                # Nếu vai trò không nằm trong ROLE_CHOICES, áp dụng mapping
                if original_role not in [choice[0] for choice in ProjectUser.ROLE_CHOICES]:
                    if original_role in role_mapping:
                        member_data['role_in_project'] = role_mapping[original_role]
                        print(f"Đã map vai trò {original_role} -> {member_data['role_in_project']}")
                    else:
                        # Nếu không có mapping, sử dụng 'Member' làm default
                        member_data['role_in_project'] = 'Member'
                        print(f"Vai trò {original_role} không hợp lệ, sử dụng 'Member'")
                
                # Tạo context chứa project
                context = {'project': project}
                
                # Sử dụng AddProjectMemberSerializer
                member_serializer = AddProjectMemberSerializer(
                    data=member_data,
                    context=context
                )
                
                if member_serializer.is_valid():
                    member_serializer.save()
                    print(f"Đã thêm thành công thành viên: {member_data['user_id']}")
                else:
                    print(f"Lỗi khi validate thành viên: {member_serializer.errors}")
            except Exception as e:
                print(f"Lỗi không xác định khi thêm thành viên: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Đảm bảo lấy dữ liệu mới nhất của project
        updated_project = self.get_queryset().get(project_id=project.project_id)
        
        # Trả về response
        return Response(
            self.get_serializer(updated_project).data,
            status=status.HTTP_201_CREATED
        )
