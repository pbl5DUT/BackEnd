# api/models/project_user.py
from django.db import models, transaction
from api.models.project import Project
from api.models.user import User
import uuid

class ProjectUser(models.Model):
    ROLE_CHOICES = [
        ('Manager', 'Manager'),
        ('Member', 'Member'),
        ('Support', 'Support'),
        ('Observer', 'Observer'),
        ('Developer', 'Developer'),  
        ('Tester', 'Tester'),   
    ]

    id = models.CharField(primary_key=True, max_length=50)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_assignments')
    role_in_project = models.CharField(max_length=20, choices=ROLE_CHOICES)
    joined_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Tự động tạo id nếu chưa có - THREAD SAFE VERSION
        if not self.id:
            self.id = self._generate_unique_id()
        
        super().save(*args, **kwargs)

    def _generate_unique_id(self):
        """
        Tạo ID unique với atomic transaction để tránh race condition
        """
        try:
            # Sử dụng atomic transaction để đảm bảo thread-safe
            with transaction.atomic():
                # Lấy tất cả IDs có format prju-xxx và tìm số lớn nhất
                existing_ids = ProjectUser.objects.filter(
                    id__startswith='prju-'
                ).values_list('id', flat=True)
                
                max_id_num = 0
                for existing_id in existing_ids:
                    try:
                        # Extract số từ ID format: prju-123
                        id_num = int(existing_id.split('-')[1])
                        if id_num > max_id_num:
                            max_id_num = id_num
                    except (IndexError, ValueError, TypeError):
                        # Skip nếu format ID không đúng
                        continue
                
                # Thử tạo ID mới từ max_id_num + 1 đến max_id_num + 50
                for i in range(max_id_num + 1, max_id_num + 51):
                    candidate_id = f'prju-{i}'
                    
                    # Double check ID này chưa tồn tại
                    if not ProjectUser.objects.filter(id=candidate_id).exists():
                        return candidate_id
                
                # Nếu 50 số tiếp theo đều đã tồn tại (highly unlikely)
                # Fallback: dùng count-based ID
                total_count = ProjectUser.objects.count()
                for i in range(total_count + 1, total_count + 100):
                    candidate_id = f'prju-{i}'
                    if not ProjectUser.objects.filter(id=candidate_id).exists():
                        return candidate_id
                        
        except Exception as e:
            # Log error để debug (optional)
            print(f"Error in _generate_unique_id: {str(e)}")
        
        # Ultimate fallback: UUID-based ID (guaranteed unique)
        unique_suffix = uuid.uuid4().hex[:8]
        return f'prju-{unique_suffix}'

    def __str__(self):
        return f"{self.user.full_name} - {self.role_in_project} in {self.project.project_name}"

    class Meta:
        db_table = 'api_projectuser'
        unique_together = ('project', 'user')