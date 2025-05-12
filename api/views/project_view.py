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
    
    @action(detail=True, methods=['post'])
    def members(self, request, project_id=None):
        """
        Thêm thành viên vào project
        URL: POST /api/projects/{project_id}/members/
        """
        try:
            project = self.get_object()
        except Project.DoesNotExist:
            return Response(
                {"error": "Project không tồn tại"}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        serializer = AddProjectMemberSerializer(data=request.data, context={'project': project})
        
        if serializer.is_valid():
            project_user = serializer.save()
            return Response(
                ProjectUserSerializer(project_user).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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

    # Ghi đè list để có thể trả về dự án với thông tin thành viên
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
     # api/views/project_view.py
    # api/views/project_view.py
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