# api/views/auth_view.py
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from api.models.user import User
from django.contrib.auth.hashers import check_password

class LoginView(APIView):
    def post(self, request):
        # Lấy email và mật khẩu từ dữ liệu yêu cầu
        email = request.data.get('email')
        password = request.data.get('password')

        # Truy vấn người dùng theo email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found with this email")

        # Kiểm tra mật khẩu
        if not user.check_password(password):  # So sánh mật khẩu đã mã hóa
            raise AuthenticationFailed("Invalid credentials, please try again")

        # Tạo refresh token và access token
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        # Trả về tokens cho người dùng
        return Response({
            'access_token': str(access_token),
            'refresh_token': str(refresh),
        }, status=status.HTTP_200_OK)
