# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.report_view import WorkReportViewSet
from api.views.user_projects_view import UserProjectsViewSet
from api.views.user_view import UserViewSet
from api.views.project_view import ProjectViewSet
from api.views.task_view import TaskViewSet
from api.views.team_view import TeamViewSet
from api.views.task_category_view import TaskCategoryViewSet
from api.views.auth_view import LoginView
from api.views.auth_check_view import AuthCheckView
from api.views.chatroom_views import ChatRoomViewSet
from api.views.message_views import MessageViewSet
from api.views.register_view import RegisterView
from api.views.sendgrid_email import send_password_email
from .views import check_email
from api.views import calendar_views as views
from .views import NotificationViewSet
from api.views.chatbot_view import chat_with_gpt
from rest_framework_nested import routers

# Khởi tạo Default Router
router = DefaultRouter()

# Đăng ký các ViewSets vào router
router.register(r'users', UserViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'teams', TeamViewSet)
router.register(r'chatrooms', ChatRoomViewSet)
router.register(r'messages', MessageViewSet)
router.register(r'notifications', NotificationViewSet, basename='notification')

# WorkReport API
router.register(r'workreports', WorkReportViewSet)

# Nested routers cho các tính năng bổ sung
project_router = routers.NestedDefaultRouter(router, r'projects', lookup='project')
project_router.register(r'task-categories', TaskCategoryViewSet, basename='project-task-categories')

task_category_router = routers.NestedDefaultRouter(project_router, r'task-categories', lookup='category')
task_category_router.register(r'tasks', TaskViewSet, basename='category-tasks')

user_router = routers.NestedDefaultRouter(router, r'users', lookup='user')
user_router.register(r'projects', UserProjectsViewSet, basename='user-projects')

# URL patterns cho API
urlpatterns = [
    path('', include(router.urls)),  # Bao gồm các URL từ DRF router
    path('', include(user_router.urls)),
    path('', include(project_router.urls)),
    path('', include(task_category_router.urls)),

    # Các route khác như đăng ký và đăng nhập
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('send-password-email/', send_password_email, name='send_password_email'),
    path('check-email/', check_email.check_email_exists, name='check_email_exists'),

    # Calendar API routes
    path('calendar/events', views.events),
    path('calendar/events/project/<str:project_id>', views.get_events_by_project),
    path('calendar/events/my-events', views.get_user_events),
    path('calendar/events/upcoming', views.get_upcoming_events),
    path('calendar/events/<str:event_id>/update', views.update_event, name='update_event'),
    path('calendar/events/<str:event_id>/delete', views.delete_event, name='delete_event'),
    path('calendar/sync/google', views.sync_google_calendar),


    # Chức năng chatbot
    path('chat/', chat_with_gpt),
    path("chat/", chat_with_gpt),
    path('messages/upload_attachment/', MessageViewSet.as_view({'post': 'upload_attachment'})),
\
]
