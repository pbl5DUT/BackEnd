from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.user_view import UserViewSet
from api.views.project_view import ProjectViewSet
from api.views.task_view import TaskViewSet
from api.views.team_view import TeamViewSet
from api.views.task_category_view import TaskCategoryViewSet
from api.views.auth_view import LoginView
from api.views.register_view import RegisterView

from rest_framework_nested import routers

# Khởi tạo router
router = DefaultRouter()

# Đăng ký viewset với router
router.register(r'users', UserViewSet)
router.register(r'projects', ProjectViewSet)  # Đảm bảo chỉ đăng ký 1 lần
router.register(r'tasks', TaskViewSet)
router.register(r'teams', TeamViewSet)

# Nested router: task-categories là con của projects
project_router = routers.NestedDefaultRouter(router, r'projects', lookup='project')
project_router.register(r'task-categories', TaskCategoryViewSet, basename='project-task-categories')

# Thêm các endpoint tùy chỉnh vào urlpatterns
urlpatterns = [
    path('', include(router.urls)),  # Kết hợp các URL từ router
    path('', include(project_router.urls)),  # Nested router cho task-categories
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
]
