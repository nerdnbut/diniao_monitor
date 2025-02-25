from django.db import models


class AlarmTask(models.Model):
    """报警任务模型"""

    ALARM_TYPES = [
        ('cpu', 'CPU 使用率'),
        ('memory', '内存使用率'),
        ('disk', '磁盘空间'),
        ('network', '网络带宽'),
    ]

    ALARM_LEVELS = [
        ('high', '高'),
        ('medium', '中'),
        ('low', '低'),
    ]

    ALARM_STATUSES = [
        ('triggered', '已触发'),
        ('resolved', '已处理'),
        ('pending', '待处理'),
    ]

    serverId = models.ForeignKey('server_management.Server', on_delete=models.CASCADE, related_name='alarm_tasks', verbose_name="服务器")
    alarmType = models.CharField(choices=ALARM_TYPES, max_length=10, verbose_name="报警类型")
    alarmLevel = models.CharField(choices=ALARM_LEVELS, max_length=10, verbose_name="报警级别")
    threshold = models.FloatField(verbose_name="报警阈值")
    current_value = models.FloatField(null=True, blank=True, verbose_name="当前值")  # 存储当前监控值（可选）
    status = models.CharField(choices=ALARM_STATUSES, default='pending', max_length=10, verbose_name="报警状态")
    message = models.TextField(null=True, blank=True, verbose_name="报警信息")  # 用于存储报警的详细信息或描述
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        # return f"{self.server.name} - {self.alarm_type} - {self.alarm_level}"
        return f"{self.serverId}"
