# api/serializers/enterprise_serializer.py

from rest_framework import serializers
from api.models.enterprise import Enterprise

class EnterpriseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enterprise
        fields = ['enterprise_id', 'Name', 'Address', 'PhoneNumber', 'Email', 'Industry']
        # Sửa 'EnterpriseID' thành 'enterprise_id' để phù hợp với cột trong database