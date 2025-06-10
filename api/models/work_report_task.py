# api/models/work_report_task.py
from django.db import models
from api.models.work_report import WorkReport  # Đảm bảo rằng bạn có đường dẫn chính xác tới WorkReport
from api.models.task import Task  # Đảm bảo rằng bạn có đường dẫn chính xác tới Task

class WorkReportTask(models.Model):
    # Khóa ngoại liên kết với WorkReport (Báo cáo công việc)
    report = models.ForeignKey(WorkReport, on_delete=models.CASCADE, related_name='workreport_tasks')
    
    # Khóa ngoại liên kết với Task (Công việc)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    
    # Bạn có thể thêm các trường bổ sung cho bảng trung gian nếu cần
    assigned_date = models.DateTimeField(auto_now_add=True)  # Thêm ngày được phân công
    completed_date = models.DateTimeField(null=True, blank=True)  # Ngày hoàn thành công việc (nếu có)

    # Một số trường bổ sung tùy thuộc vào yêu cầu của bạn
    status = models.CharField(max_length=20, choices=[('TODO', 'To Do'), ('IN_PROGRESS', 'In Progress'), ('DONE', 'Done')], default='TODO')
    
    def __str__(self):
        return f"{self.report.title} - {self.task.task_name}"

    class Meta:
        db_table = 'api_workreport_task'  # Đặt tên bảng trong cơ sở dữ liệu
        verbose_name = "Work Report Task"
        verbose_name_plural = "Work Report Tasks"
