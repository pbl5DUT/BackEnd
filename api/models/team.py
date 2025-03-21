# api/models/team.py

from django.db import models
from .user import User
from .project import Project

class Team(models.Model):
    team_id = models.AutoField(primary_key=True)
    team_name = models.CharField(max_length=255)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    leader = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.team_name
