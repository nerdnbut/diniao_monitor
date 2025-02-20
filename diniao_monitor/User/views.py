from django.contrib.auth import login, authenticate
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import make_password
from sendemail import *
import json
import re

from . import models
from .models import User


@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data['username']
            password = data['password']
            email = data['email']
            captcha = data['captcha']

            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': '用户名已存在'}, status=400)
            # 验证邮箱是否存在
            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': '邮箱已存在'}, status=411)
            # 验证邮箱格式
            pattern = r'@[a-zA-Z0-9]+\.[a-zA-Z]+$'
            if not re.search(pattern, email):
                return JsonResponse({'error': '请输入正确的邮箱'}, status=422)
            # 验证验证码
            captcha_code = code[0]
            if captcha == '' or captcha_code != captcha:
                return JsonResponse({'error': '请先获取验证码'}, status=433)

            user = User.objects.create(
                username=username,
                email=email,
                password=make_password(password)
            )
            user.save()
            code[0] = ''
            return JsonResponse({'message': '用户注册成功'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


# 登录
@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data['username']
            password = data['password']
            # 验证用户是否存在
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if not user.check_password(password):
                    return JsonResponse({'error': '密码错误'}, status=444)
                else:
                    login(request, user)
                    # 获取或创建用户的 Token
                    token, created = Token.objects.get_or_create(user=user)
                    response = JsonResponse({
                        'message': '登录成功',
                        'username': user.username,
                        'token': token.key  # 返回生成的 Token
                    }, status=200)
                    response.set_cookie('session_id', request.session.session_key, httponly=True)
                    return response
            else:
                return JsonResponse({'error': '用户名不存在'}, status=444)
        except Exception as e:
            print(e)
            return JsonResponse({'error': '服务器错误'}, status=500)
    else:
        return JsonResponse({'error': '请求方法无效'}, status=405)


# 修改密码
@csrf_exempt
# @login_required
def revise_password(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            password = data['password']
            email = data['email']
            captcha = data['captcha']
            user = User.objects.get(email=email)
            # 如果password判断相同则修改password
            if code[0] == captcha:
                user.password = make_password(password)
                user.save()
                code[0] = ''
                return JsonResponse({'message': '操作成功'}, status=201)
            elif captcha == '' or code[0] != captcha:
                return JsonResponse({'error': '验证码错误'}, status=444)
        except Exception as e:
            print(e)
            return JsonResponse({'error': '原始密码错误'}, status=444)


# 修改邮箱
@csrf_exempt
def revise_email(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data['email']
            newemail = data['newemail']
            captcha = data['captcha']
            user = User.objects.get(email=email)
            # 如果验证码正确则修改email
            if code[0] == captcha:
                user.email = newemail
                user.save()
                code[0] = ''
                return JsonResponse({'message': '操作成功'}, status=201)
            elif captcha == '' or code[0] != captcha:
                return JsonResponse({'error': '验证码错误'}, status=444)
        except Exception as e:
            print(e)
            return JsonResponse({'error': '原始邮箱错误'}, status=444)
