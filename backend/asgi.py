import os

# Đặt DJANGO_SETTINGS_MODULE trước khi import bất kỳ thứ gì từ Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Import Django ASGI application sau khi cài đặt settings
from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

# Import các module channels sau khi Django được khởi tạo
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from api.middleware import TokenAuthMiddlewareStack
import api.routing

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': TokenAuthMiddlewareStack(
        URLRouter(
            api.routing.websocket_urlpatterns
        )
    ),
})