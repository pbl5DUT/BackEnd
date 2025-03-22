from api.serializers.enterprise_serializer import EnterpriseSerializer
from rest_framework import serializers
from api.models.user import User
from api.models.enterprise import Enterprise

class UserSerializer(serializers.ModelSerializer):
    enterprise = EnterpriseSerializer()  # Thêm trường doanh nghiệp vào UserSerializer

    class Meta:
        model = User
        fields = ['user_id', 'full_name', 'email', 'password', 'role', 'department', 'created_at', 'enterprise']

    def create(self, validated_data):
        # Tạo doanh nghiệp trước
        enterprise_data = validated_data.pop('enterprise')
        enterprise = Enterprise.objects.create(**enterprise_data)

        # Lấy mật khẩu từ validated_data
        password = validated_data.pop('password')

        # Tạo user sau khi doanh nghiệp đã được tạo
        user = User.objects.create(enterprise=enterprise, **validated_data)

        # Mã hóa mật khẩu trước khi lưu
        user.set_password(password)
        user.save()

        return user
