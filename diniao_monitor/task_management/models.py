from django.db import models
from server_management.models import Server

class ScheduledTask(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='scheduled_tasks')
    script_name = models.CharField(max_length=255)
    script_type = models.CharField(max_length=20, choices=[('python', 'Python Script'), ('shell', 'Shell Script')])
    script_path = models.CharField(max_length=1024)  # 保存脚本的路径
    execute_time = models.DateTimeField()
    execute_count = models.IntegerField(default=1)
    is_recurring = models.BooleanField(default=False)  # 是否循环执行

    def __str__(self):
        return self.script_name
 