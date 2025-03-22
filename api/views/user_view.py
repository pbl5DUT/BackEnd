# api/views/user_view.py

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from ..models.user import User
from ..serializers.user_serializer import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # Thêm phương thức tìm kiếm người dùng theo email
    @staticmethod
    def get_user_by_email(email):
        """Tìm người dùng theo email."""
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None