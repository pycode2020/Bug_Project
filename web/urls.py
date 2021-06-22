from django.conf.urls import url, include
from web.views import account
from web.views import home
from web.views import project

urlpatterns = [
    # 注册
    url(r'^register/$', account.register, name='register'),  # 添加name 方便反向解析
    # 短信验证
    url(r'^send/sms/$', account.send_sms, name='send_sms'),
    # 短信登录
    url(r'^login/sms/$', account.login_sms, name='login_sms'),
    # 用户登录
    url(r'^login/$', account.login, name='login'),
    # 退出登录
    url(r'^logout/$', account.logout, name='logout'),
    # 获取图片验证码地址
    url(r'^img/code/$', account.image_code, name='image_code'),
    # 首页
    url(r'^index/$', home.index, name='index'),

    # 项目管理
    url(r'^project/list$',project.project_list, name='project_list'),

]
