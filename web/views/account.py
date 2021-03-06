"""
用户账号相关的功能：注册，短信，登录，注销
"""
from django.shortcuts import render, HttpResponse, redirect
from web.forms.account import RegisterModelForm, SendSmsForm, LoginSMSFrom, LoginFrom
from django.http import JsonResponse
from django_redis import get_redis_connection
from web import models
from web.views import home
import uuid
import datetime
import web.models



def register(request):
    """注册页面"""
    if request.method == 'GET':
        form = RegisterModelForm()
        return render(request, 'register.html', {'form': form})

    # 获取POST数据进行校验
    form = RegisterModelForm(data=request.POST)
    if form.is_valid():  # is.valid()让form进行校验
        # 验证通过后，写入用户表中（注册）
        instance = form.save()
        # 获取免费版价格策略
        policy_object = models.PricePolicy.objects.filter(category=1, title='个人免费版').first()

        # 方式一：注册时创建交易记录 方式二，不写，注释 方式一
        models.Transaction.objects.create(
            status=2,
            order=str(uuid.uuid4()),  # 随机字符串
            user=instance,
            price_policy=policy_object,
            count=0,
            price=0,
            start_datetime=datetime.datetime.now()
        )

        return JsonResponse({'status': True, 'data': '/login/'})
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
        return JsonResponse({'status': True, 'code': redis_str_code})
    return JsonResponse({'status': False, 'error': form.errors})


def login_sms(request):
    """ 短信登录 """
    if request.method == 'GET':
        form = LoginSMSFrom()
        return render(request, 'login_sms.html', {'form': form})
    form = LoginSMSFrom(request.POST)
    if form.is_valid():
        # 用户输入校验正确
        mobile_phone = form.cleaned_data['mobile_phone']
        # 用户信息存放入session
        user_object = models.UserInfo.objects.filter(mobile_phone=mobile_phone).first()
        request.session['user_id'] = user_object.id
        request.session['user_name'] = user_object.username

        return JsonResponse({'status': True, 'data': '/index/'})
    return JsonResponse({'status': False, 'error': form.errors})


def login(request):
    """用户名和密码登录"""
    if request.method == 'GET':
        form = LoginFrom(request)
        return render(request, 'login.html', {'form': form})

    form = LoginFrom(request, data=request.POST)
    if form.is_valid():
        # 获取用户名和密码
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']

        # 用户名或邮箱或手机号登录 Q查询
        from django.db.models import Q
        # 获取数据库用户数据
        # user_object = models.UserInfo.objects.filter(username=username, password=password).first()
        # 获取数据库用户或手机或邮箱数据
        user_object = models.UserInfo.objects.filter(
            Q(username=username) | Q(email=username) | Q(mobile_phone=username)).filter(
            password=password).first()

        # 校验用户名和密码
        if user_object:
            # 登录成功保存用户session 信息
            request.session['user_id'] = user_object.id
            # session过期时间
            request.session.set_expiry(60 * 60 * 24 * 2)  # 秒/分/时/天

            return redirect('index')
        # 校验错误，把错误信息添加到from
        form.add_error('username', '用户名密码错误')

    return render(request, 'login.html', {'form': form})


def logout(request):
    # 清空session数据
    request.session.flush()
    return redirect('index')


def image_code(request):
    """ 生成图片验证码"""
    from utils.image_code import check_code
    img_object, code = check_code()

    # 保存至 session
    request.session['image_code'] = code
    request.session.set_expiry(60)  # 主动修改session 超时时间60秒，默认为2周

    # 将图片写到内存中
    from io import BytesIO
    stream = BytesIO()
    img_object.save(stream, 'png')
    stream.getvalue()

    return HttpResponse(stream.getvalue())
