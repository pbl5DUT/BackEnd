# api/views/register_view.py

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from api.serializers.user_serializer import UserSerializer

class RegisterView(APIView):
    def post(self, request):
        # Lấy dữ liệu từ yêu cầu
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            # Lưu thông tin người dùng và doanh nghiệp vào cơ sở dữ liệu
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
