from django.urls import path
from .views import register_user, login_user, revise_password, revise_email  # , check_session
from sendemail import control_generation

urlpatterns = [
    # 注册
    path('api/register/', register_user, name='register_user'),
    # 登录
    path('api/login/', login_user, name='login_user'),
    # 检测是否登录
    # path('api/check_session/', check_session, name='check_session'),
    # 发送验证码
    path('api/email_verify/', control_generation, name='control_generation'),
    # 修改密码
    path('api/revise_password/', revise_password, name='revise_password'),
    # 修改邮箱
    path('api/revise_email/', revise_email, name='revise_email'),
]
