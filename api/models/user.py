# models/user.py
import bcrypt
from django.db import models
from api.models.enterprise import Enterprise

class User(models.Model):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Manage', 'Manage'),
        ('User', 'User'),
    ]

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    user_id = models.CharField(primary_key=True, max_length=50)
    full_name = models.CharField(max_length=255)
    
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=60)
    role = models.CharField(choices=ROLE_CHOICES, max_length=20, default='User')
    department = models.CharField(max_length=255, blank=True, null=True)
    
    gender = models.CharField(choices=GENDER_CHOICES, max_length=10, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    province = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    position = models.CharField(max_length=255, blank=True, null=True)
    avatar = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    # Simplemente usar ForeignKey sin especificar to_field
    enterprise = models.ForeignKey(Enterprise, db_column='enterprise_id', on_delete=models.CASCADE, related_name='users')

    def set_password(self, raw_password):
        """
        Mã hóa mật khẩu gốc và lưu vào `password`.
        """
        salt = bcrypt.gensalt(rounds=12)
        self.password = bcrypt.hashpw(raw_password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, raw_password):
        """
        Kiểm tra mật khẩu người dùng nhập vào với mật khẩu đã băm.
        """
        return bcrypt.checkpw(raw_password.encode('utf-8'), self.password.encode('utf-8'))

    def save(self, *args, **kwargs):
        # Tạo user_id định dạng 'user-{id}' nếu chưa được thiết lập
        if not self.user_id:
            # Truy vấn trực tiếp để tìm ID lớn nhất từ tất cả user_id
            from django.db import connection
            
            with connection.cursor() as cursor:
                cursor.execute("SELECT MAX(CAST(SUBSTRING(user_id, 6) AS UNSIGNED)) FROM api_user")
                result = cursor.fetchone()[0]
                
                # Nếu không có kết quả (bảng trống) hoặc lỗi, bắt đầu từ 1
                if result is None:
                    next_id = 1
                else:
                    next_id = result + 1
                    
                self.user_id = f'user-{next_id}'
                print(f"Tạo user_id mới: {self.user_id}")
        
        # Đảm bảo created_at luôn có giá trị
        if not self.created_at:
            from django.utils import timezone
            self.created_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        """
        Always return True for custom User model.
        This is used by DRF for permission checks.
        """
        return True

    def __str__(self):
        return self.full_name

    class Meta:
        db_table = 'api_user'