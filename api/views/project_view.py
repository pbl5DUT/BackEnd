# api/views/project_view.py
from rest_framework import viewsets
from ..models.project import Project
from ..serializers.project_serializer import ProjectSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
