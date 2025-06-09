from rest_framework import viewsets
from api.models import Notification
from api.serializers import NotificationSerializer
from rest_framework.permissions import IsAuthenticated

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Chỉ trả thông báo gửi tới người đang đăng nhập
        return Notification.objects.filter(sent_to=self.request.user).order_by('-sent_date')
