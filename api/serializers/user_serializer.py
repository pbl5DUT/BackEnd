from rest_framework import serializers
from api.models.user import User
from api.models.enterprise import Enterprise
from api.serializers.enterprise_serializer import EnterpriseSerializer


class UserSerializer(serializers.ModelSerializer):
    enterprise = EnterpriseSerializer()  # Serialize nested object

    class Meta:
        model = User
        fields = [
            'user_id', 'full_name', 'email', 'password', 'role', 'department',
            'gender', 'birth_date', 'phone', 'province', 'district', 'address',
            'position', 'avatar', 'created_at', 'enterprise'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        # Pop nested enterprise data
        enterprise_data = validated_data.pop('enterprise')
        enterprise = Enterprise.objects.create(**enterprise_data)

        # Handle password separately
        raw_password = validated_data.pop('password')
        user = User(enterprise=enterprise, **validated_data)
        user.set_password(raw_password)
        user.save()

        return user
