# api/serializers/enterprise_serializer.py
from rest_framework import serializers
from api.models.enterprise import Enterprise

class EnterpriseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enterprise
        fields = ['enterprise_id', 'name', 'address', 'phone_number', 'email', 'industry', 'created_at', 'updated_at']
        # Các trường thêm vào read_only để tránh người dùng sửa đổi
        extra_kwargs = {
            'enterprise_id': {'required': False},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }