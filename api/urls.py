from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.register_view import RegisterView
from api.views.user_view import UserViewSet
from api.views.project_view import ProjectViewSet
from api.views.auth_view import LoginView

# Khởi tạo router
router = DefaultRouter()

# Đăng ký viewset với router
router.register(r'users', UserViewSet)
router.register(r'projects', ProjectViewSet)


# Thêm các endpoint tùy chỉnh vào urlpatterns
# urlpatterns = router.urls + [
#     path('register/', RegisterView.as_view(), name='register'),
#     path('login/', LoginView.as_view(), name='login'),
# ]

# Thêm các endpoint tùy chỉnh vào urlpatterns
urlpatterns = [
    path('', include(router.urls)),  # Kết hợp các URL từ router
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
]