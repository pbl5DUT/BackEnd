# api/views/__init__.py

from .user_view import UserViewSet  # Đảm bảo bạn đã import đúng
from .project_view import ProjectViewSet
# from .task_view import TaskViewSet
# from .comment_view import CommentViewSet
from .register_view import RegisterView
from .auth_view import LoginView
from .sendgrid_email import send_password_email