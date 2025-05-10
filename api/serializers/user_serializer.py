# api/serializers/user_serializer.py
from rest_framework import serializers
from api.models.user import User
from api.models.enterprise import Enterprise
from api.serializers.enterprise_serializer import EnterpriseSerializer

class UserSerializer(serializers.ModelSerializer):
    enterprise = EnterpriseSerializer(read_only=True)  # Chỉ đọc
    enterprise_id = serializers.CharField(write_only=True, required=False)  # Thêm trường này để nhận ID
    
    class Meta:
        model = User
        fields = [
            'user_id', 'full_name', 'email', 'password', 'role', 'department',
            'gender', 'birth_date', 'phone', 'province', 'district', 'address',
            'position', 'avatar', 'created_at', 'enterprise', 'enterprise_id'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'user_id': {'required': False},
            'created_at': {'read_only': True}
        }

    def create(self, validated_data):
        # Lấy enterprise_id từ dữ liệu đã xác thực
        enterprise_id = validated_data.pop('enterprise_id', None)
        
        # Tìm enterprise dựa trên ID
        if enterprise_id:
            try:
                enterprise = Enterprise.objects.get(enterprise_id=enterprise_id)
            except Enterprise.DoesNotExist:
                raise serializers.ValidationError({'enterprise_id': 'Enterprise không tồn tại'})
        else:
            # Sử dụng enterprise mặc định nếu không có ID
            try:
                enterprise = Enterprise.objects.get(enterprise_id='ent-1')
            except Enterprise.DoesNotExist:
                raise serializers.ValidationError({'enterprise_id': 'Không tìm thấy enterprise mặc định'})
        
        # Xử lý password
        raw_password = validated_data.pop('password')
        
        # Tạo user
        user = User(enterprise=enterprise, **validated_data)
        user.set_password(raw_password)
        user.save()

        return user
    
    def update(self, instance, validated_data):
        # Xử lý enterprise_id nếu được cung cấp
        enterprise_id = validated_data.pop('enterprise_id', None)
        if enterprise_id:
            try:
                instance.enterprise = Enterprise.objects.get(enterprise_id=enterprise_id)
            except Enterprise.DoesNotExist:
                raise serializers.ValidationError({'enterprise_id': 'Enterprise không tồn tại'})
        
        # Xử lý password nếu được cung cấp
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        
        # Cập nhật các trường khác
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance