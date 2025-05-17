# api/models/task_category.py
from django.db import models
from api.models.project import Project
from django.db import connection

class TaskCategory(models.Model):
    id = models.CharField(primary_key=True, max_length=50)
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='categories',
        db_column='project_id'
    )
    tasks_count = models.IntegerField(default=0)
    completed_tasks_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Tự động tạo id nếu chưa có
        if not self.id:
            # Sử dụng truy vấn SQL trực tiếp để lấy ID lớn nhất
            with connection.cursor() as cursor:
                cursor.execute("SELECT MAX(CAST(SUBSTRING(id, 5) AS UNSIGNED)) FROM api_taskcategory")
                result = cursor.fetchone()[0]
                
                # Nếu không có kết quả hoặc lỗi, bắt đầu từ 1
                if result is None:
                    next_id = 1
                else:
                    next_id = result + 1
                    
                self.id = f'cat-{next_id}'
                print(f"Tạo task category id mới: {self.id}")
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name or f"Category {self.id}"  # Đảm bảo không gặp lỗi nếu name là None

    class Meta:
        db_table = 'api_taskcategory'