from django.conf.urls import url, include
from web.views import account

urlpatterns = [
    # 注册
    url(r'^register/', account.register, name='register'),#添加name 方便反向解析
]
