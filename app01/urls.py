from django.conf.urls import url,include
from django.contrib import admin
from app01 import views

urlpatterns = [
    # 模拟短信验证
    url(r'^send/sms/', views.send_sms),
    # 注册页面,
    # 由于上级路由添加添加namespace='app01',所以反向解析为”app01:register“
    url(r'^register/', views.register,name='register'),
]