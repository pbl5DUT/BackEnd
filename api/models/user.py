# api/models/user.py

from django.db import models
# api/models/user.py
from api.models.enterprise import Enterprise

class User(models.Model):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('User', 'User'),
    ]
    
    user_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=254, unique=True)
    password_hash = models.CharField(max_length=255)
    role = models.CharField(choices=ROLE_CHOICES, max_length=20)
    department = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Create a default Enterprise or provide some fallback logic
    enterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE, default=1)  # Assuming you have an Enterprise with ID 1

    def __str__(self):
        return self.full_name
