"""
用户账号相关的功能：注册，短信，登录，注销
"""
from django.shortcuts import render, HttpResponse
from web.forms.account import RegisterModelForm, SendSmsForm
from django.http import JsonResponse


def register(request):
    """注册页面f"""
    form = RegisterModelForm()
    return render(request, 'register.html', {'from': form})


def send_sms(request):
    """发送短信验证"""
    print(request.GET)
    mobile_phone = request.GET.get('mobile_phone')
    tple = request.GET.get('register')
    # 实例化SendSmsForm
    form = SendSmsForm(request, data=request.GET)
    # print(form.clean_mobile_phone.code)
    # form.is_valid只是校验手机号码，不能为空，格式是否正确
    if form.is_valid():
        return JsonResponse({'status': True})
    return JsonResponse({'status': False,'error':form.errors})

    # # 实例化SendSmsForm
    # form = SendSmsForm(request,data=request.GET)
    # # form.is_valid只是校验手机号码，不能为空，格式是否正确
    # if form.is_valid():
    #     # 发短信
    #     # 写入redis
    #     return JsonResponse({'status':True,'code':form.code})
    # return JsonResponse({'status':False,'error':form.errors})
