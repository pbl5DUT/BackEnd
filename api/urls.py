from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.register_view import RegisterView
from api.views.user_projects import UserProjectsAPIView
from api.views.user_view import UserViewSet
from api.views.project_view import ProjectViewSet
from api.views.auth_view import LoginView
from api.views.auth_check_view import AuthCheckView
from api.views.chatroom_views import ChatRoomViewSet
from api.views.message_views import MessageViewSet

# Khởi tạo router
router = DefaultRouter()

# Đăng ký viewset với router
router.register(r'users', UserViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'chatrooms', ChatRoomViewSet)
router.register(r'messages', MessageViewSet)



# Thêm các endpoint tùy chỉnh vào urlpatterns
urlpatterns = [
    path('', include(router.urls)),  # Kết hợp các URL từ router
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    

]   