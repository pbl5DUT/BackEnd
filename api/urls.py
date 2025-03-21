from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from .views import UserViewSet, UserListView, UserDetailView
from .views import UserViewSet, ProjectViewSet, TaskViewSet, CommentViewSet

# Khởi tạo router
router = DefaultRouter()

# Đăng ký viewset với router
router.register(r'users', UserViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'comments', CommentViewSet)

# Thêm các endpoint tùy chỉnh vào urlpatterns
urlpatterns = router.urls 