# api/models/task_comment.py
from django.db import models
from api.models.user import User
from api.models.task import Task

class TaskComment(models.Model):
    id = models.CharField(primary_key=True, max_length=50)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments',
        db_column='task_id'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='task_comments',
        db_column='user_id'
    )
    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        db_column='parent_comment_id'
    )

    def save(self, *args, **kwargs):
        # Tự động tạo id nếu chưa có
        if not self.id:
            last_comment = TaskComment.objects.all().order_by('-id').first()
            if last_comment:
                try:
                    last_id = int(last_comment.id.split('-')[1])
                    self.id = f'comment-{last_id + 1}'
                except (IndexError, ValueError):
                    self.id = 'comment-1'
            else:
                self.id = 'comment-1'
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Comment by {self.user} on {self.task}'

    class Meta:
        db_table = 'api_taskcomment'