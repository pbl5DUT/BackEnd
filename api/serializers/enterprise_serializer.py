# api/serializers/enterprise_serializer.py

from rest_framework import serializers
from api.models.enterprise import Enterprise

class EnterpriseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enterprise
        fields = ['EnterpriseID', 'Name', 'Address', 'PhoneNumber', 'Email', 'Industry']
