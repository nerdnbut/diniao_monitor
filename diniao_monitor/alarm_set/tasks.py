from celery import shared_task
from alarm_set.models import AlarmTask
from server_management.models import Server
from email.utils import formataddr
from server_management.server_resource import cpu, mem, Network, swp
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def get_server_credentials(task):
    """从任务中提取服务器凭证"""
    server = task.serverId
    return server.ip_address, server.user, server.port, server.get_password()


def send_email(subject, message, recipient_email):
    """发送电子邮件通知"""
    sender_email = formataddr(["Diniao", 'nerdnbut@qq.com'])  # 填写你的发送邮箱
    sender_password = ""  # 填写你的邮箱密码
    smtp_server = "smtp.qq.com"  # 填写SMTP服务器地址

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = "Dinoamonitor通知：" + subject
    msg.attach(MIMEText(message, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, 587)  # SMTP端口号
        server.starttls()  # 启用TLS加密
        server.login("nerdnbut@qq.com", sender_password)
        print(f"邮箱登录成功,密码为{sender_password}")
        server.sendmail("nerdnbut@qq.com", recipient_email, msg.as_string())
        server.quit()
        print(f"报警邮件已发送至 {recipient_email}")
    except Exception as e:
        print(f"发送邮件失败: {e}")


def handle_alarm(task, current_value, threshold, alarm_type, message):
    """处理报警逻辑"""
    task.current_value = current_value
    task.save()
    if current_value >= threshold:
        trigger_alarm(task, message)


def trigger_alarm(task, message):
    print('task:', task)
    """执行报警操作，例如发送邮件"""
    print(f"触发报警: {task.serverId.name} - {message}")
    recipient_email = "a1529572511@gmail.com"  # 填写接收报警的邮箱
    send_email(f"{task.serverId.name} - {message}", message, recipient_email)
    # 修改任务状态
    task.status = 'triggered'
    task.save()


from datetime import datetime

@shared_task
def fetch_server_data_and_check_alarms():
    print(f"报警任务执行时间: {datetime.now()}")
    # 获取所有 状态为pending的报警任务
    alarm_tasks = AlarmTask.objects.filter(status='pending')

    for task in alarm_tasks:
        try:
            ip, user, port, password = get_server_credentials(task)

            # 获取资源使用情况
            cpu_usage = cpu.run_cpu(ip, user, password, port)
            mem_usage = mem.run_mem(ip, user, password, port)
            swp_usage = swp.run_swp(ip, user, password, port)
            network_usage = Network.run_network(ip, user, password, port)

            # 计算网络带宽使用率
            total_network_usage = 0
            for iface, rate in network_usage.items():
                total_network_usage += rate['rx_rate'] + rate['tx_rate']
            network_usage_percentage = min((total_network_usage / (1024 * 1024)) * 100, 100)  # 转换为MB/s并限制最大值为100%

            if task.alarmType == 'cpu':
                handle_alarm(task, cpu_usage, task.threshold, 'cpu', f'CPU使用率超过{task.threshold}%')
            elif task.alarmType == 'memory':
                handle_alarm(task, mem_usage, task.threshold, 'memory', f'内存使用率超过{task.threshold}%')
            elif task.alarmType == 'disk':
                handle_alarm(task, swp_usage, task.threshold, 'disk', f'磁盘使用率超过{task.threshold}%')
            elif task.alarmType == 'network':
                handle_alarm(task, network_usage_percentage, task.threshold, 'network', f'网络带宽使用率超过{task.threshold}%')
        
        except Exception as e:
            print(f"无法登录到服务器 {task.serverId.name}: {e}")
            continue  # 跳过当前任务