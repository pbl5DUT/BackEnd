import bcrypt
from django.db import models
from api.models.enterprise import Enterprise

class User(models.Model):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('User', 'User'),
    ]
    
    user_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=60)  # bcrypt hash có độ dài cố định là 60
    role = models.CharField(choices=ROLE_CHOICES, max_length=20)
    department = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    enterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE, default=1)

    def set_password(self, raw_password):
        """
        Mã hóa mật khẩu gốc và lưu vào `password`.
        """
        salt = bcrypt.gensalt(rounds=12)  # Tạo salt với số vòng cụ thể
        self.password = bcrypt.hashpw(raw_password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, raw_password):
        """
        Kiểm tra mật khẩu người dùng nhập vào với mật khẩu đã băm.
        """
        # Dùng bcrypt để kiểm tra mật khẩu
        return bcrypt.checkpw(raw_password.encode('utf-8'), self.password.encode('utf-8'))

    def __str__(self):
        return self.full_name
