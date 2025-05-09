from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from api.models.user import User
from django.contrib.auth.hashers import check_password

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found with this email")

        if not user.check_password(password):
            raise AuthenticationFailed("Invalid credentials, please try again")

        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        # Trả về access_token, refresh_token và user info (gồm role)
        return Response({
            'access_token': str(access_token),
            'refresh_token': str(refresh),
            'user': {
                'user_id': user.user_id,
                'full_name': user.full_name,
                'email': user.email,
                'role': user.role,  # 👉 thêm role trả ra cho frontend
            }
        }, status=status.HTTP_200_OK)
