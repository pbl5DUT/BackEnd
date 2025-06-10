# api/views/__init__.py

from .user_view import UserViewSet  # Đảm bảo bạn đã import đúng
from .project_view import ProjectViewSet
# from .task_view import TaskViewSet
# from .comment_view import CommentViewSet
from .register_view import RegisterView
from .auth_view import LoginView
from .sendgrid_email import send_password_email
from .check_email import check_email_exists
from .calendar_views import (
    events,
    get_events_by_project,
    get_user_events,
    update_event,
    delete_event,
    get_upcoming_events,
    sync_google_calendar,
)
from .notification import NotificationViewSet
from .chatAI_view import ask_question
