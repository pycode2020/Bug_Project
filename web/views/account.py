"""
用户账号相关的功能：注册，短信，登录，注销
"""
from django.shortcuts import render, HttpResponse
from web.forms.account import RegisterModelForm


def register(request):
    form = RegisterModelForm()
    return render(request, 'register.html', {'from': form})
