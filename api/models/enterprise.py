# api/models/enterprise.py

from django.db import models

class Enterprise(models.Model):
    EnterpriseID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=255)
    Address = models.CharField(max_length=255)
    PhoneNumber = models.CharField(max_length=50)
    Email = models.EmailField(max_length=254)
    Industry = models.CharField(max_length=100, blank=True, null=True)  # Thêm blank=True và null=True

    def __str__(self):
        return self.Name
