# api/serializers/user_serializer.py

from api.serializers.enterprise_serializer import EnterpriseSerializer
from rest_framework import serializers
from api.models.user import User
from api.models.enterprise import Enterprise

class UserSerializer(serializers.ModelSerializer):
    enterprise = EnterpriseSerializer()  # Thêm trường doanh nghiệp vào UserSerializer

    class Meta:
        model = User
        fields = ['user_id', 'full_name', 'email', 'password_hash', 'role', 'department', 'created_at', 'enterprise']

    def create(self, validated_data):
        # Tạo doanh nghiệp trước
        enterprise_data = validated_data.pop('enterprise')
        enterprise = Enterprise.objects.create(**enterprise_data)

        # Tạo user sau khi doanh nghiệp đã được tạo
        user = User.objects.create(enterprise=enterprise, **validated_data)
        return user
