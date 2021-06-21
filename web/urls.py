from django.conf.urls import url, include
from web.views import account
from web.views import home

urlpatterns = [
    # 注册
    url(r'^register/$', account.register, name='register'),#添加name 方便反向解析
    # 短信验证
    url(r'^send/sms/$', account.send_sms, name='send_sms'),
    # 短信登录
    url(r'^login/sms/$', account.login_sms, name='login_sms'),
    # 用户登录
    url(r'^login/$', account.login, name='login'),
    # 获取图片验证码地址
    url(r'^img/code/$', account.image_code, name='image_code'),
    # 首页
    url(r'^index/$',home.index, name='index'),
]
