import random
import string
import time
import threading
import smtplib
from django.http import JsonResponse
from email.mime.text import MIMEText
from email.utils import formataddr
from django.views.decorators.csrf import csrf_exempt
import json
import re
from User.models import User

stop_event = threading.Event()
code = ['']


# 生成随机验证码
def generate_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


# 发送邮件
def display_code():
    global code
    while not stop_event.is_set():
        code[0] = generate_code()
        time.sleep(120)


# 控制验证码生成
@csrf_exempt
def control_generation(request):
    global stop_event
    global code_thread
    global code

    if request.method == 'POST':
        data = json.loads(request.body)
        action = data.get('action')
        email = data.get('email')

        if action == 'runemail':
            stop_event.set()
            if not stop_event.is_set():
                # 如果线程已经在运行，直接返回成功
                return True
            else:
                # 否则，启动新的线程
                stop_event.clear()
                code_thread = threading.Thread(target=display_code)
                code_thread.start()
                # 验证邮箱格式
                pattern = r'@[a-zA-Z0-9]+\.[a-zA-Z]+$'
                if not re.search(pattern, email):
                    return JsonResponse({'error': '请输入正确的邮箱'}, status=422)
                email_send(email)
                return JsonResponse({'success': '操作成功'}, status=201)

        elif action == 'stopemail':
            if not stop_event.is_set():
                # 停止线程
                stop_event.set()
                # 等待线程结束
                # code_thread.join()

        elif action == 'revise_get_code':
            # 验证邮箱格式
            pattern = r'@[a-zA-Z0-9]+\.[a-zA-Z]+$'
            if not re.search(pattern, email):
                return JsonResponse({'error': '请输入正确的邮箱'}, status=444)
            if User.objects.filter(email=email).exists():
                stop_event.set()
                if not stop_event.is_set():
                    # 如果线程已经在运行，直接返回成功
                    return True
                else:
                    # 否则，启动新的线程
                    stop_event.clear()
                    code_thread = threading.Thread(target=display_code)
                    code_thread.start()
                    email_send(email)
                    return JsonResponse({'success': '操作成功'}, status=201)
            else:
                return JsonResponse({'error': '邮箱不存在'}, status=444)


# 发送邮箱信息
def email_send(email):
    global code
    # 发送邮件
    try:
        msg = MIMEText('验证码：%s' % code[0], 'plain', 'utf-8')
        msg['From'] = formataddr(["Diniao", '312121231@qq.com'])
        msg['To'] = formataddr(["您好尊敬的的：", email])
        msg['Subject'] = "Dinoamonitor"
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)
        server.login("312121231@qq.com", "icwrewrvvhdafdcjch")
        server.sendmail('312121231@qq.com', [email], msg.as_string())
        server.quit()
    except Exception as e:
        print(e)
        return False  # 发送失败
