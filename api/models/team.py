# api/models/team.py
from django.db import models
from api.models.user import User
from api.models.project import Project

class Team(models.Model):
    team_id = models.CharField(primary_key=True, max_length=50)
    team_name = models.CharField(max_length=255)
    leader = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='led_teams',
        db_column='leader_id'
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='teams',
        db_column='project_id'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Tự động tạo team_id nếu chưa có
        if not self.team_id:
            last_team = Team.objects.all().order_by('-team_id').first()
            if last_team:
                try:
                    last_id = int(last_team.team_id.split('-')[1])
                    self.team_id = f'team-{last_id + 1}'
                except (IndexError, ValueError):
                    self.team_id = 'team-1'
            else:
                self.team_id = 'team-1'
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.team_name

    class Meta:
        db_table = 'api_team'