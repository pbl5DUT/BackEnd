# api/views/project_member_views.py
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from api.models.project import Project
from api.models.project_user import ProjectUser
from api.serializers.project_member_serializer import AddProjectMemberSerializer
from api.serializers.project_user_serializer import ProjectUserSerializer

class ProjectViewSet(ModelViewSet):
    # Thêm action để quản lý thành viên
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        project = self.get_object()
        serializer = AddProjectMemberSerializer(data=request.data, context={'project': project})
        
        if serializer.is_valid():
            project_user = serializer.save()
            return Response(
                ProjectUserSerializer(project_user).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'])
    def remove_member(self, request, pk=None):
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