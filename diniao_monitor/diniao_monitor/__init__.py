from __future__ import absolute_import, unicode_literals

# 这样 Django 会在启动时加载 Celery 应用
from .celery import app as celery_app

__all__ = ('celery_app',)
