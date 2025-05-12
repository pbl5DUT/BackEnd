# # from django.shortcuts import render

# # # Create your views here.
# # from rest_framework import viewsets
# # from .models import User
# # from .serializers import UserSerializer

# # from rest_framework.views import APIView
# # from rest_framework.response import Response
# # from rest_framework import status
# # from .models import User
# # from .serializers import UserSerializer

# # class UserViewSet(viewsets.ModelViewSet):
# #     queryset = User.objects.all()
# #     serializer_class = UserSerializer



# # # API liệt kê tất cả người dùng
# # class UserListView(APIView):
# #     def get(self, request):
# #         users = User.objects.all()
# #         serializer = UserSerializer(users, many=True)
# #         return Response(serializer.data)

# # # API chi tiết người dùng
# # class UserDetailView(APIView):
# #     def get(self, request, id):
# #         try:
# #             user = User.objects.get(id=id)
# #         except User.DoesNotExist:
# #             return Response(status=status.HTTP_404_NOT_FOUND)
        
# #         serializer = UserSerializer(user)
# #         return Response(serializer.data)

# from rest_framework import viewsets
# from .models import User, Project, Task, Comment
# from .serializers import UserSerializer, ProjectSerializer, TaskSerializer, CommentSerializer

# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

# class ProjectViewSet(viewsets.ModelViewSet):
#     queryset = Project.objects.all()
#     serializer_class = ProjectSerializer

# class TaskViewSet(viewsets.ModelViewSet):
#     queryset = Task.objects.all()
#     serializer_class = TaskSerializer

# class CommentViewSet(viewsets.ModelViewSet):
#     queryset = Comment.objects.all()
#     serializer_class = CommentSerializer