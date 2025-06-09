from rest_framework.response import Response
from api.models.project_user import ProjectUser
from api.models.project import Project
from api.serializers import ProjectSerializer
from rest_framework import viewsets


class UserProjectsViewSet(viewsets.ViewSet): # type: ignore
    def list(self, request, user_pk=None):
        # Lấy danh sách các project_id mà user đang tham gia
        project_ids = ProjectUser.objects.filter(user__user_id=user_pk).values_list('project_id', flat=True)

        # Lấy danh sách Project tương ứng
        projects = Project.objects.filter(project_id__in=project_ids).distinct()

        # Serialize và trả về
        serializer = ProjectSerializer(projects, many=True)
        return Response({
            "count": projects.count(),
            "projects": serializer.data
        })
