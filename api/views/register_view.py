from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from api.serializers.user_serializer import UserSerializer
from api.models.user import User

class RegisterView(APIView):
    def post(self, request):
        # Lấy dữ liệu từ yêu cầu
        email = request.data.get('email')

        # Kiểm tra xem email đã tồn tại trong cơ sở dữ liệu chưa
        if User.objects.filter(email=email).exists():
            return Response({"message": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

        # Sử dụng serializer để kiểm tra tính hợp lệ của dữ liệu
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            # Lưu người dùng sau khi đã mã hóa mật khẩu trong serializer
            user = serializer.save()  # Mật khẩu đã được mã hóa trong phương thức create của serializer
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        
        # Trả về lỗi nếu serializer không hợp lệ
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
