"""
用户账号相关的功能：注册，短信，登录，注销
"""
from django.shortcuts import render, HttpResponse
from web.forms.account import RegisterModelForm, SendSmsForm
from django.http import JsonResponse
from django_redis import get_redis_connection


def register(request):
    """注册页面"""
    if request.method == 'GET':
        form = RegisterModelForm()
        return render(request, 'register.html', {'from': form})

    # 获取POST数据进行校验
    form = RegisterModelForm(data=request.POST)
    if form.is_valid(): # is.valid()让form进行校验
        # 验证通过后，写入数据库
        instance = form.save()
        return JsonResponse({'status':True,'data':'/login/'})
    else:
        #  .errors 校验失败的错误信息
        return JsonResponse({'status': False, 'error': form.errors})


def send_sms(request):
    """发送短信验证"""
    # print(request.GET)
    mobile_phone = request.GET.get('mobile_phone')
    tple = request.GET.get('register')
    # 实例化SendSmsForm
    form = SendSmsForm(request, data=request.GET)
    # print(form.clean_mobile_phone.code)
    # form.is_valid只是校验手机号码，不能为空，格式是否正确
    if form.is_valid():
        # redis 获取验证码
        conn = get_redis_connection()
        redis_code = conn.get(mobile_phone)
        redis_str_code = redis_code.decode('utf-8')
        print('验证码：', redis_code)
        return JsonResponse({'status': True,'code':redis_str_code})
    return JsonResponse({'status': False,'error':form.errors})