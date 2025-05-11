# api/serializers/team_serializer.py
from rest_framework import serializers
from api.models.team import Team
from api.models.team_user import TeamUser
from api.models.user import User
from api.models.project import Project
from api.serializers.user_serializer import UserSerializer
from api.serializers.team_user_serializer import TeamUserSerializer

class TeamSerializer(serializers.ModelSerializer):
    leader = UserSerializer(read_only=True)
    leader_id = serializers.CharField(write_only=True, required=False)
    members = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = [
            'team_id', 'team_name', 'leader', 'leader_id',
            'project', 'created_at', 'updated_at', 'members'
        ]
        extra_kwargs = {
            'team_id': {'required': False},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
            'project': {'write_only': True}
        }
    
    def get_members(self, obj):
        # Lấy tất cả thành viên của team
        team_users = TeamUser.objects.filter(team=obj)
        return TeamUserSerializer(team_users, many=True).data
    
    def create(self, validated_data):
        # Xử lý leader_id nếu được cung cấp
        leader_id = validated_data.pop('leader_id', None)
        
        if leader_id:
            try:
                leader = User.objects.get(user_id=leader_id)
            except User.DoesNotExist:
                raise serializers.ValidationError({'leader_id': 'Leader không tồn tại'})
        else:
            leader = None
            
        # Kiểm tra project
        project_id = validated_data.get('project')
        if project_id:
            try:
                project = Project.objects.get(project_id=project_id)
                validated_data['project'] = project
            except Project.DoesNotExist:
                raise serializers.ValidationError({'project': 'Project không tồn tại'})
        
        # Tạo team
        team = Team(leader=leader, **validated_data)
        team.save()
        
        # Nếu có leader, tạo TeamUser với role là Lead
        if leader:
            TeamUser.objects.create(
                team=team,
                user=leader,
                role_in_team='Lead'
            )
        
        return team
    
    def update(self, instance, validated_data):
        # Xử lý leader_id nếu được cung cấp
        leader_id = validated_data.pop('leader_id', None)
        
        if leader_id:
            try:
                new_leader = User.objects.get(user_id=leader_id)
                
                # Cập nhật leader trong team
                instance.leader = new_leader
                
                # Kiểm tra xem leader mới đã là thành viên của team chưa
                team_user, created = TeamUser.objects.get_or_create(
                    team=instance,
                    user=new_leader,
                    defaults={'role_in_team': 'Lead'}
                )
                
                # Nếu đã là thành viên nhưng không phải Lead, cập nhật role
                if not created and team_user.role_in_team != 'Lead':
                    team_user.role_in_team = 'Lead'
                    team_user.save()
                
                # Cập nhật các Lead cũ thành Member
                TeamUser.objects.filter(
                    team=instance, 
                    role_in_team='Lead'
                ).exclude(
                    user=new_leader
                ).update(role_in_team='Member')
                
            except User.DoesNotExist:
                raise serializers.ValidationError({'leader_id': 'Leader không tồn tại'})
        
        # Cập nhật các trường khác
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance