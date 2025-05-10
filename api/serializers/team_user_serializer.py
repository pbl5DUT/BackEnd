# api/serializers/team_user_serializer.py
from rest_framework import serializers
from api.models.team_user import TeamUser
from api.models.user import User
from api.models.team import Team
from api.serializers.user_serializer import UserSerializer

class TeamUserSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = TeamUser
        fields = ['id', 'role_in_team', 'team', 'user', 'created_at']
        extra_kwargs = {
            'id': {'required': False},
            'created_at': {'read_only': True},
            'team': {'write_only': True}
        }

class AddTeamMemberSerializer(serializers.Serializer):
    user_id = serializers.CharField(required=True)
    role_in_team = serializers.ChoiceField(
        choices=TeamUser.ROLE_CHOICES,
        default='Member'
    )
    
    def validate_user_id(self, value):
        try:
            User.objects.get(user_id=value)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError('User không tồn tại')
    
    def create(self, validated_data):
        team = self.context.get('team')
        user_id = validated_data.get('user_id')
        role_in_team = validated_data.get('role_in_team')
        
        # Kiểm tra xem user đã là thành viên của team chưa
        user = User.objects.get(user_id=user_id)
        
        # Kiểm tra xem user đã là thành viên của team chưa
        if TeamUser.objects.filter(team=team, user=user).exists():
            raise serializers.ValidationError('User đã là thành viên của team')
        
        # Nếu role là Lead, cập nhật leader của team và chuyển các Lead khác thành Member
        if role_in_team == 'Lead':
            # Cập nhật leader của team
            team.leader = user
            team.save()
            
            # Chuyển các Lead khác thành Member
            TeamUser.objects.filter(team=team, role_in_team='Lead').update(role_in_team='Member')
        
        # Tạo TeamUser mới
        team_user = TeamUser.objects.create(
            team=team,
            user=user,
            role_in_team=role_in_team
        )
        
        return team_user