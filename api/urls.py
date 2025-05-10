from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.register_view import RegisterView
from api.views.task_category_view import TaskCategoryViewSet
from api.views.task_view import TaskViewSet
from api.views.team_view import TeamViewSet
from api.views.user_projects import UserProjectsAPIView
from api.views.user_view import UserViewSet
from api.views.project_view import ProjectViewSet
from api.views.auth_view import LoginView

from rest_framework_nested import routers

# Khởi tạo router
router = DefaultRouter()

# Đăng ký viewset với router
router.register(r'users', UserViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'categories', TaskCategoryViewSet)
router.register(r'teams', TeamViewSet)


# Thêm các endpoint tùy chỉnh vào urlpatterns
# urlpatterns = router.urls + [
#     path('register/', RegisterView.as_view(), name='register'),
#     path('login/', LoginView.as_view(), name='login'),
# ]

# Nested router: task-categories là con của projects
project_router = routers.NestedDefaultRouter(router, r'projects', lookup='project')
project_router.register(r'task-categories', TaskCategoryViewSet, basename='project-task-categories')

# Thêm các endpoint tùy chỉnh vào urlpatterns
urlpatterns = [


    path('', include(router.urls)),  # Kết hợp các URL từ router
    path('', include(project_router.urls)), 
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    # path('users/<int:user_id>/projects/', UserProjectsAPIView.as_view(), name='user-projects'),
]