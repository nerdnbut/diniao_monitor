import os
import paramiko
from django.http import JsonResponse
from django.utils import timezone
from .models import ScheduledTask, Server
from datetime import datetime, timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ScheduledTaskSerializer
from dateutil import parser
from rest_framework import status

# 上传脚本并在服务器执行
def upload_to_server(server_ip, username, password, script_path):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server_ip, username=username, password=password)

        # 上传脚本
        remote_script_path = "/tmp/" + os.path.basename(script_path)
        script_name = os.path.splitext(os.path.basename(script_path))[0]
        sftp = ssh.open_sftp()
        try:
            sftp.put(script_path, remote_script_path)
        except Exception as e:
            print(str(e))
        sftp.close()
        ssh.close()
        return remote_script_path,script_name
    except Exception as e:
        return str(e), ''

# 创建 cron 任务
def create_cron_job(server_ip, username, password, script_path, execute_time, script_type,is_recurring,script_name):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server_ip, username=username, password=password)

        ssh.exec_command(f"chmod +x {script_path}")
         # 创建日志文件并赋予写入权限
        log_file = f"/tmp/{script_name}.log"
        ssh.exec_command(f"touch {log_file}")
        ssh.exec_command(f"chmod 666 {log_file}")  # 所有用户可读写
        # 格式化执行时间为 cron 格式
        # 根据是否循环生成不同的cron时间表达式
        if is_recurring:
            cron_time = execute_time.strftime('%M %H * * *')  # 每天执行
        else:
            cron_time = execute_time.strftime('%M %H %d %m *')  # 单次执行，指定日期和月份
        
        #判断脚本类型
        if(script_type == 'shell'):
            cron_job = f"{cron_time} bash {script_path} >> {log_file} 2>&1"
        else:
            cron_job = f"{cron_time} /usr/bin/python3 {script_path} >> {log_file} 2>&1"
            # cron_job = f"* * * * * /usr/bin/python3 {script_path} >> {log_file} 2>&1"

        # 创建 cron 任务
        cron_command = f"(crontab -l; echo '{cron_job}') | crontab -"
        stdin, stdout, stderr = ssh.exec_command(cron_command)
        error_output = stderr.read().decode()
        if error_output:
            ssh.close()
            return f"Error creating cron job: {error_output}"
        ssh.close()
        return f"Successfully created cron job: {cron_job}"
    except Exception as e:
        return f"Error creating cron job: {e}"

# 新增上传脚本接口
@api_view(['POST'])
def upload_script(request):
    """上传脚本文件并返回文件路径"""
    if request.FILES.get('file'):
        script_file = request.FILES['file']
        script_name = script_file.name
        # 保存脚本到本地
        script_dir = '/tmp/scripts'
        os.makedirs(script_dir, exist_ok=True)
        script_path = os.path.join(script_dir, script_name)

        with open(script_path, 'wb') as f:
            for chunk in script_file.chunks():
                f.write(chunk)

        return JsonResponse({'status': 'success', 'script_path': script_path})

    return JsonResponse({'status': 'error', 'message': 'No script file uploaded.'})

# 新增定时任务接口
@api_view(['POST'])
def create_scheduled_task(request):
    """创建定时任务"""
    if request.method == 'POST':
        server_id = request.data.get('server_id')
        script_path = request.data.get('script_path')
        execute_time = request.data.get('execute_time')
        is_recurring = request.data.get('is_recurring') == 'true'
        script_type = request.data.get('script_type')

        # 解析执行时间
        execute_time = parser.parse(execute_time)
        now = timezone.now()
        # 判断执行时间是否已过
        if now > execute_time:
            execute_time = execute_time + timedelta(days=1)
        
        # 查找服务器
        server = Server.objects.get(id=server_id)

        # 上传脚本到服务器,并返回脚本在服务器的路径
        server_script_path, script_name = upload_to_server(
            server.ip_address, server.user, server.get_password(), script_path
        )
        # 创建 ScheduledTask 记录
        task = ScheduledTask.objects.create(
            server=server,
            script_name=os.path.basename(script_path),
            script_type=script_type,
            script_path=script_path,
            execute_time=execute_time,
            is_recurring=is_recurring
        )
        # 设置 cron 任务
        create_cron_job(server.ip_address, server.user, server.get_password(), server_script_path, execute_time, script_type,is_recurring,script_name)

        return JsonResponse({'status': 'success', 'task_id': task.id})

    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})

@api_view(['GET'])
def list_scheduled_tasks(request):
    """获取所有定时任务的列表"""
    tasks = ScheduledTask.objects.all()
    serializer = ScheduledTaskSerializer(tasks, many=True)
    return Response(serializer.data)

# 删除定时任务接口
@api_view(['DELETE'])
def delete_scheduled_task(request, task_id):
    """删除定时任务"""
    try:
        task = ScheduledTask.objects.get(id=task_id)
        task.delete()
        return Response({'status': 'success', 'message': '任务删除成功'}, status=status.HTTP_204_NO_CONTENT)
    except ScheduledTask.DoesNotExist:
        return Response({'status': 'error', 'message': '任务不存在'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
