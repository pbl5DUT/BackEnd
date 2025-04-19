from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.models.project import Project
from api.serializers.project_serializer import ProjectSerializer

class UserProjectsAPIView(APIView):
    def get(self, request, user_id):
        projects = Project.objects.filter(projectuser__user_id=user_id).distinct()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
       