# api/models/team_user.py

from django.db import models
from .team import Team
from .user import User

class TeamUser(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role_in_team = models.CharField(choices=[('Member', 'Member'), ('Lead', 'Lead'), ('Support', 'Support')], max_length=20)

    class Meta:
        unique_together = ('team', 'user')

    def __str__(self):
        return f"{self.user} - {self.team} - {self.role_in_team}"
