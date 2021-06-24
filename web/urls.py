from django.conf.urls import url, include
from web.views import account
from web.views import home
from web.views import project
from web.views import manage
from web.views import wiki

urlpatterns = [
    # 注册
    url(r'^register/$', account.register, name='register'),  # 添加name 方便反向解析
    # 短信验证
    url(r'^send/sms/$', account.send_sms, name='send_sms'),
    # 短信登录
    url(r'^login/sms/$', account.login_sms, name='login_sms'),
    # 用户登录
    url(r'^login/$', account.login, name='login'),
    # 获取图片验证码地址
    url(r'^img/code/$', account.image_code, name='image_code'),
    # 首页
    url(r'^index/$', home.index, name='index'),

    # 退出登录
    url(r'^logout/$', account.logout, name='logout'),

    # 项目列表
    url(r'^project/list/$', project.project_list, name='project_list'),
    # 添加星标 /project/star/my/1 /project/star/join/1
    url(r'^project/star/(?P<project_type>\w+)/(?P<project_id>\d+)/$', project.project_star, name='project_star'),
    # 取消星标
    url(r'^project/unstar/(?P<project_type>\w+)/(?P<project_id>\d+)/$', project.project_unstar, name='project_unstar'),

    # 进入项目管理
    url(r'^manage/(?P<project_id>\d+)/', include([
        url(r'^dashboard/$', manage.dashboard, name='manage_dashboard'),
        url(r'^issues/$', manage.issues, name='manage_issues'),
        url(r'^statistics/$', manage.statistics, name='manage_statistics'),
        url(r'^file/$', manage.file, name='manage_file'),
        url(r'^wiki/$', wiki.wiki, name='manage_wiki'),
        url(r'^setting/$', manage.setting, name='manage_setting'),
    ], None)),
]
