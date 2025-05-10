# api/models/team_user.py
from django.db import models
from api.models.user import User
from api.models.team import Team

class TeamUser(models.Model):
    ROLE_CHOICES = [
        ('Lead', 'Lead'),
        ('Member', 'Member'),
        ('Support', 'Support'),
    ]
    
    id = models.CharField(primary_key=True, max_length=50)
    role_in_team = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='Member'
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='members',
        db_column='team_id'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='team_memberships',
        db_column='user_id'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Tự động tạo id nếu chưa có
        if not self.id:
            last_team_user = TeamUser.objects.all().order_by('-id').first()
            if last_team_user:
                try:
                    last_id = int(last_team_user.id.split('-')[1])
                    self.id = f'teamuser-{last_id + 1}'
                except (IndexError, ValueError):
                    self.id = 'teamuser-1'
            else:
                self.id = 'teamuser-1'
                
        # Nếu role_in_team là Lead, cập nhật leader của team
        if self.role_in_team == 'Lead':
            self.team.leader = self.user
            self.team.save()
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user} as {self.role_in_team} in {self.team}'

    class Meta:
        db_table = 'api_teamuser'
        unique_together = ('team', 'user')  # Mỗi user chỉ có thể có một vai trò trong team