# api/views/team_view.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from api.models.team import Team
from api.models.team_user import TeamUser
from api.serializers.team_serializer import TeamSerializer
from api.serializers.team_user_serializer import TeamUserSerializer, AddTeamMemberSerializer

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    lookup_field = 'team_id'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['team_name']
    ordering_fields = ['team_name', 'created_at']
    
    def get_queryset(self):
        queryset = Team.objects.all()
        
        # Lọc theo project_id
        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(project__project_id=project_id)
            
        # Lọc theo leader_id
        leader_id = self.request.query_params.get('leader_id')
        if leader_id:
            queryset = queryset.filter(leader__user_id=leader_id)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def members(self, request, team_id=None):
        """
        Lấy danh sách thành viên của team
        URL: GET /api/teams/{team_id}/members/
        """
        team = self.get_object()
        team_users = TeamUser.objects.filter(team=team)
        serializer = TeamUserSerializer(team_users, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, team_id=None):
        """
        Thêm thành viên vào team
        URL: POST /api/teams/{team_id}/add_member/
        """
        team = self.get_object()
        
        serializer = AddTeamMemberSerializer(data=request.data, context={'team': team})
        if serializer.is_valid():
            team_user = serializer.save()
            return Response(
                TeamUserSerializer(team_user).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'])
    def remove_member(self, request, team_id=None):
        """
        Xóa thành viên khỏi team
        URL: DELETE /api/teams/{team_id}/remove_member/?user_id={user_id}
        """
        team = self.get_object()
        user_id = request.query_params.get('user_id')
        
        if not user_id:
            return Response(
                {"error": "user_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            team_user = TeamUser.objects.get(team=team, user__user_id=user_id)
            
            # Không cho phép xóa leader khi team chỉ có một thành viên
            if team_user.role_in_team == 'Lead' and TeamUser.objects.filter(team=team).count() <= 1:
                return Response(
                    {"error": "Cannot remove the only leader of the team"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Nếu xóa leader, cập nhật lại leader của team
            if team_user.role_in_team == 'Lead':
                # Đặt leader của team thành None
                team.leader = None
                team.save()
            
            team_user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except TeamUser.DoesNotExist:
            return Response(
                {"error": "User is not a member of this team"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['patch'])
    def update_member_role(self, request, team_id=None):
        """
        Cập nhật vai trò của thành viên trong team
        URL: PATCH /api/teams/{team_id}/update_member_role/
        """
        team = self.get_object()
        user_id = request.data.get('user_id')
        role = request.data.get('role_in_team')
        
        if not user_id or not role:
            return Response(
                {"error": "user_id and role_in_team fields are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if role not in dict(TeamUser.ROLE_CHOICES):
            return Response(
                {"error": f"role_in_team must be one of {dict(TeamUser.ROLE_CHOICES).keys()}"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            team_user = TeamUser.objects.get(team=team, user__user_id=user_id)
            
            # Nếu thay đổi vai trò thành Lead, cập nhật leader của team và chuyển các Lead khác thành Member
            if role == 'Lead' and team_user.role_in_team != 'Lead':
                # Cập nhật leader của team
                team.leader = team_user.user
                team.save()
                
                # Chuyển các Lead khác thành Member
                TeamUser.objects.filter(team=team, role_in_team='Lead').exclude(user=team_user.user).update(role_in_team='Member')
            
            # Nếu thay đổi vai trò từ Lead thành khác, đặt leader của team thành None nếu không còn Lead nào khác
            if team_user.role_in_team == 'Lead' and role != 'Lead':
                if TeamUser.objects.filter(team=team, role_in_team='Lead').count() <= 1:
                    team.leader = None
                    team.save()
            
            team_user.role_in_team = role
            team_user.save()
            
            return Response(TeamUserSerializer(team_user).data)
        except TeamUser.DoesNotExist:
            return Response(
                {"error": "User is not a member of this team"},
                status=status.HTTP_404_NOT_FOUND
            )