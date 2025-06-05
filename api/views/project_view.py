# api/views/project_view.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from api.models.project import Project
from api.models.project_user import ProjectUser
from api.models.user import User  # Thêm import User để validate
from api.serializers.project_serializer import ProjectSerializer
from api.serializers.project_member_serializer import AddProjectMemberSerializer
from api.serializers.project_user_serializer import ProjectUserSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    lookup_field = 'project_id'  # Sử dụng project_id thay vì pk mặc định
    
    @action(detail=True, methods=['get', 'post', 'delete'])
    def members(self, request, project_id=None):
        """
        Quản lý members của project
        GET: Lấy danh sách members
        POST: Thêm member mới
        """
        if request.method == 'GET':
            return self._get_members(request, project_id)
        elif request.method == 'POST':
            return self._add_member(request, project_id)
        elif request.method == 'DELETE':
            return self.remove_member(request, project_id)
    
    def _get_members(self, request, project_id):
        """Lấy danh sách members của project"""
        try:
            project = self.get_object()
            members = ProjectUser.objects.filter(project=project).select_related('user')
            
            return Response(
                {
                    "project_id": project.project_id,
                    "project_name": project.project_name,
                    "members_count": members.count(),
                    "members": ProjectUserSerializer(members, many=True).data
                },
                status=status.HTTP_200_OK
            )
        except Project.DoesNotExist:
            return Response(
                {"error": f"Project với ID '{project_id}' không tồn tại"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def _add_member(self, request, project_id):
        """Thêm member vào project với validation đầy đủ"""
        print(f"=== THÊM MEMBER VÀO PROJECT ===")
        print(f"Request data: {request.data}")
        print(f"Project ID: {project_id}")
        
        # 1. Validate input data
        user_id = request.data.get('user_id')
        role_in_project = request.data.get('role_in_project')
        
        if not user_id:
            return Response(
                {"error": "user_id là bắt buộc"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not role_in_project:
            return Response(
                {"error": "role_in_project là bắt buộc"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 2. Kiểm tra project tồn tại
        try:
            project = self.get_object()
            print(f"✓ Project found: {project.project_id} - {project.project_name}")
        except Project.DoesNotExist:
            print("✗ Project not found!")
            return Response(
                {"error": f"Project với ID '{project_id}' không tồn tại"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 3. Kiểm tra user tồn tại
        try:
            user = User.objects.get(user_id=user_id)
            print(f"✓ User found: {user.user_id} - {user.full_name}")
        except User.DoesNotExist:
            print(f"✗ User not found: {user_id}")
            return Response(
                {"error": f"User với ID '{user_id}' không tồn tại"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 4. KIỂM TRA USER ĐÃ LÀ MEMBER CHƯA (QUAN TRỌNG!)
        print(f"→ Checking if user {user_id} is already a member...")
        existing_member = ProjectUser.objects.filter(
            project=project, 
            user=user
        ).first()
        
        print(f"→ Query: ProjectUser.objects.filter(project={project.project_id}, user={user.user_id})")
        print(f"→ Existing member found: {existing_member}")
        
        if existing_member:
            print(f"✗ User đã là member: {existing_member.role_in_project}")
            print(f"✗ Member ID: {existing_member.id}")
            print(f"✗ Joined date: {existing_member.joined_date}")
            return Response(
                {
                    "error": f"User '{user.full_name}' đã là member của project này",
                    "current_role": existing_member.role_in_project,
                    "joined_date": existing_member.joined_date,
                    "member_id": existing_member.id,
                    "suggestion": "Sử dụng API update để thay đổi role hoặc xóa member trước khi thêm lại"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        print(f"✓ User chưa là member, có thể thêm mới")
        
        # 5. Validate role hợp lệ
        valid_roles = [choice[0] for choice in ProjectUser.ROLE_CHOICES]
        if role_in_project not in valid_roles:
            print(f"✗ Invalid role: {role_in_project}")
            return Response(
                {
                    "error": f"Role '{role_in_project}' không hợp lệ",
                    "valid_roles": valid_roles
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 6. Tạo member mới TRỰC TIẾP (bypass serializer để tránh update logic)
        print(f"→ Creating new member DIRECTLY...")
        
        try:
            # Kiểm tra lần cuối trước khi create
            final_check = ProjectUser.objects.filter(project=project, user=user).exists()
            if final_check:
                print(f"✗ RACE CONDITION: User vừa được thêm bởi request khác!")
                return Response(
                    {"error": "User đã là member (race condition detected)"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Tạo ProjectUser trực tiếp
            project_user = ProjectUser.objects.create(
                project=project,
                user=user, 
                role_in_project=role_in_project
            )
            
            print(f"✓ Member created successfully (DIRECT):")
            print(f"  - ID: {project_user.id}")
            print(f"  - User: {project_user.user.full_name} ({project_user.user.user_id})")
            print(f"  - Role: {project_user.role_in_project}")
            print(f"  - Project: {project_user.project.project_name}")
            
            return Response(
                {
                    "message": "Thêm member thành công",
                    "data": ProjectUserSerializer(project_user).data
                },
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            print(f"✗ Error creating member directly: {str(e)}")
            print(f"✗ Exception type: {type(e).__name__}")
            
            # Nếu lỗi IntegrityError → user đã tồn tại
            if 'UNIQUE constraint failed' in str(e) or 'duplicate key' in str(e).lower():
                return Response(
                    {"error": "User đã là member của project này (constraint violation)"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(
                {"error": f"Lỗi khi tạo member: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    @action(detail=True, methods=['delete'])
    def remove_member(self, request, project_id=None):
        """
        Xóa thành viên khỏi project
        URL: DELETE /api/projects/{project_id}/members/?user_id={user_id}
        """
        print(f"=== XÓA MEMBER KHỎI PROJECT ===")
        print(f"Project ID: {project_id}")
        
        try:
            project = self.get_object()
            print(f"✓ Project found: {project.project_id}")
        except Project.DoesNotExist:
            return Response(
                {"error": f"Project với ID '{project_id}' không tồn tại"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {"error": "user_id parameter là bắt buộc"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        print(f"User ID to remove: {user_id}")
        
        try:
            project_user = ProjectUser.objects.get(project=project, user__user_id=user_id)
            
            user_name = project_user.user.full_name
            user_role = project_user.role_in_project
            
            project_user.delete()
            print(f"✓ Member removed: {user_name} ({user_role})")
            
            return Response(
                {"message": f"Đã xóa {user_name} khỏi project"},
                status=status.HTTP_200_OK
            )
        except ProjectUser.DoesNotExist:
            print(f"✗ Member not found: {user_id}")
            return Response(
                {"error": f"User '{user_id}' không phải là member của project này"},
                status=status.HTTP_404_NOT_FOUND
            )

    def retrieve(self, request, *args, **kwargs):
        """Lấy thông tin chi tiết project"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Tạo project mới (giữ nguyên logic cũ)"""
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