# api/models/enterprise.py
from django.db import models

class Enterprise(models.Model):
    enterprise_id = models.CharField(primary_key=True, max_length=50)  # Thay đổi từ EnterpriseID (AutoField) thành enterprise_id (CharField)
    name = models.CharField(max_length=255)  # Thay đổi từ Name thành name để khớp với SQL
    address = models.CharField(max_length=255)  # Thay đổi từ Address thành address
    phone_number = models.CharField(max_length=50)  # Thay đổi từ PhoneNumber thành phone_number
    email = models.EmailField(max_length=254)  # Giữ nguyên
    industry = models.CharField(max_length=100, blank=True, null=True)  # Giữ nguyên
    created_at = models.DateTimeField(auto_now_add=True)  # Thêm mới để khớp với SQL
    updated_at = models.DateTimeField(auto_now=True)  # Thêm mới để khớp với SQL

    def save(self, *args, **kwargs):
        # Tạo enterprise_id định dạng 'ent-{id}' nếu chưa được thiết lập
        if not self.enterprise_id:
            # Tìm enterprise_id lớn nhất trong database
            last_enterprise = Enterprise.objects.all().order_by('-enterprise_id').first()
            if last_enterprise:
                # Tách số từ 'ent-X' và tăng lên 1
                try:
                    last_id = int(last_enterprise.enterprise_id.split('-')[1])
                    self.enterprise_id = f'ent-{last_id + 1}'
                except (IndexError, ValueError):
                    self.enterprise_id = 'ent-1'
            else:
                self.enterprise_id = 'ent-1'
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'api_enterprise'