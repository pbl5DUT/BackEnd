from django.urls import path, include
from rest_framework.routers import DefaultRouter
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

from rest_framework_nested import routers
from api.views.sendgrid_email import send_password_email
from .views import check_email
from api.views import calendar_views as views
# Khởi tạo router
router = DefaultRouter()

# Đăng ký viewset với router
router.register(r'users', UserViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'chatrooms', ChatRoomViewSet)
router.register(r'messages', MessageViewSet)


router.register(r'projects', ProjectViewSet)  # Đảm bảo chỉ đăng ký 1 lần
router.register(r'tasks', TaskViewSet)
router.register(r'teams', TeamViewSet)

# Nested router: task-categories là con của projects
project_router = routers.NestedDefaultRouter(router, r'projects', lookup='project')
project_router.register(r'task-categories', TaskCategoryViewSet, basename='project-task-categories')


# Tạo nested router cho tasks trong project-task-categories
task_category_router = routers.NestedDefaultRouter(project_router, r'task-categories', lookup='category')
task_category_router.register(r'tasks', TaskViewSet, basename='category-tasks')

# Thêm các endpoint tùy chỉnh vào urlpatterns
urlpatterns = [
    path('', include(router.urls)),  # Kết hợp các URL từ router
    path('', include(project_router.urls)),  # Nested router cho task-categories
    path('', include(task_category_router.urls)),   
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('send-password-email/', send_password_email, name='send_password_email'),
    path('check-email/', check_email.check_email_exists, name='check_email_exists'),
    path('calendar/events', views.events),
    path('calendar/events/project/<str:project_id>', views.get_events_by_project),
    path('calendar/events/my-events', views.get_user_events),
    path('calendar/events/upcoming', views.get_upcoming_events),
    path('calendar/events/<str:event_id>/update', views.update_event, name='update_event'),
    path('calendar/events/<str:event_id>/delete', views.delete_event, name='delete_event'),
    path('calendar/sync/google', views.sync_google_calendar),
]

