# @Time    : 2025/2/13 20:47
# @Author  :      
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# 设置默认Django配置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'diniao_monitor.settings')

app = Celery('diniao_monitor')

# 使用Django的设置文件来配置Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现所有安装的app中的任务
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
