# celery beat 启动
celery -A diniao_monitor  beat -l debug

# celery worker 启动
celery -A diniao_monitor worker -l info -P eventlet