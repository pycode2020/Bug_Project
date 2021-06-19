"""
vimes.account.py 调用的form
"""

from django import forms
from web import models
from django.core.validators import RegexValidator  # 正则模块
from django.core.exceptions import ValidationError
from django_redis import get_redis_connection
import random, redis
from utils import encrypt


class BootStrapForm(object):
    """ 让下面使用BootStrapForm的类继承这个基类"""

    # 重写__init__方法，添加上默认的class类 'form-control'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            # attrs={,}属性可以添加class类样式
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = '请输入%s' % (field.label,)


class RegisterModelForm(forms.ModelForm):
    """ ModelForm生成注册页面表单字段 """
    # 对密码字段类型重写，密码插件，展示时为密文,判断密码长度，
    password = forms.CharField(label='密码',
                               min_length=6, max_length=32,
                               error_messages={
                                   'min_length': '密码长度不能小于6个字符',
                                   'max_length': '密码长度不能大于32个字符',
                               },
                               widget=forms.PasswordInput())

    # 重复确认密码； attrs={,}属性可以添加class类样式
    confirm_password = forms.CharField(label='确认密码',
                                       min_length=6, max_length=32,
                                       error_messages={
                                           'min_length': '密码长度不能小于6个字符',
                                           'max_length': '密码长度不能大于32个字符',
                                       },
                                       widget=forms.PasswordInput())

    # 对手机号码字段类型重写，进行正则判断
    mobile_phone = forms.CharField(label='手机号码', validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', '手机号格式错误'), ])

    # 验证码; attrs={,}属性可以添加class类样式
    # code = forms.CharField(label='验证码', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '验证码'}))
    code = forms.CharField(label='验证码', widget=forms.TextInput())

    class Meta:
        model = models.UserInfo
        # __all__ 前端页面form字段先自动展示models内容，然后在展示RegisterModelForm 定义后的内容
        # fields = '__all__'
        fields = ['username', 'password', 'confirm_password', 'email', 'mobile_phone', 'code']  # 自定义顺序

    # 重写__init__方法，添加上默认的class类 'form-control'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            # attrs={,}属性可以添加class类样式
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = '请输入%s' % (field.label,)

    def clean_username(self):
        """ 用户判断，不能重复 钩子 """
        username = self.cleaned_data['username']
        # 判断用户名是否存在
        exists = models.UserInfo.objects.filter(username=username).exists()
        if exists:
            raise ValidationError('用户名已存在')

        return username

    def clean_password(self):
        """密码加密 钩子"""
        pwd = self.cleaned_data['password']

        return encrypt.md5(pwd)

    def clean_confirm_password(self):
        """ 判断重复密码是否一致 钩子"""
        pwd = self.cleaned_data.get('password')
        confirm_pwd = encrypt.md5(self.cleaned_data['confirm_password'])
        if confirm_pwd != pwd:
            raise ValidationError('两次密码不一致')

        return confirm_pwd

    def clean_email(self):
        """邮箱判断，不能重复 钩子"""
        email = self.cleaned_data['email']
        # 判断用户名是否存在
        exists = models.UserInfo.objects.filter(email=email).exists()
        if exists:
            raise ValidationError('邮箱已存在')

        return email

    def clean_mobile_phone(self):
        """手机号判断，不能重复 钩子"""
        mobile_phone = self.cleaned_data['mobile_phone']
        exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if exists:
            raise ValidationError('手机号已注册')

        return mobile_phone

    def clean_code(self):
        """验证码判断，钩子"""
        code = self.cleaned_data['code']
        mobile_phone = self.cleaned_data.get('mobile_phone')
        # 获取redis中的手机号和验证码是否一致
        conn = get_redis_connection()
        redis_code = conn.get(mobile_phone)
        if not redis_code:
            raise ValidationError('验证码失效或未发送，请重新发送')
        # redis中的code是byts类型 需要转换后判断
        redis_srt_code = redis_code.decode('utf-8')
        if code.strip() != redis_srt_code:
            raise ValidationError('验证码错误，请重新输入')

        return code


class SendSmsForm(forms.Form):  # 继承forms.Form，因为ModelForm和数据库有关
    """ 校验手机号码 """
    mobile_phone = forms.CharField(label='手机号码', validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', '手机号格式错误'), ])

    def __init__(self, request, *args, **kwargs):
        """将 views.py.send_sms的request传过来"""
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_mobile_phone(self):
        """手机号码构验的钩子"""
        # 用户提交的手机号码
        mobile_phone = self.cleaned_data['mobile_phone']

        # 获取短信模板
        tpl = self.request.GET.get('tpl')

        # 校验数据库中是否存在这个手机号码
        exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        # 对短信模板登录或注册进行判断
        if tpl == 'login':
            if not exists:
                raise ValidationError('手机号码不存在')
        else:
            # 如果存在，返回以下异常
            if exists:
                # self.add_error('mobile_phone','手机号码已存在')
                raise ValidationError('手机号码已存在')  # 同上面，区别出现异常，下面不继续执行

        # 发短信 & 写入redis
        # 随机生成验证码
        code = random.randrange(1000, 9999)
        # print(code)

        # 验证码写入redis(django-redis)
        conn = get_redis_connection()  # 连接redis
        # conn = redis.Redis(host='127.0.0.1', port=6379, encoding='utf-8')
        conn.set(mobile_phone, code, ex=60)  # 超时时间为60s

        return mobile_phone


class LoginSMSFrom(BootStrapForm, forms.Form):
    """ 短信登录 """
    # 对手机号码字段类型重写，进行正则判断
    mobile_phone = forms.CharField(label='手机号码', validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', '手机号格式错误'), ])

    # 验证码; attrs={,}属性可以添加class类样式
    code = forms.CharField(label='验证码', widget=forms.TextInput())

    # 登录校验
    def clean_mobile_phone(self):
        """校验手机号码"""
        mobile_phone = self.cleaned_data['mobile_phone']
        exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        # user_object = models.UserInfo.objects.filter(mobile_phone=mobile_phone).first()

        if not exists:
            raise ValidationError('手机号码不存在')
        return mobile_phone

    def clean_code(self):
        """校验验正码"""
        mobile_phone = self.cleaned_data.get('mobile_phone')
        code = self.cleaned_data['code']
        # 获取redis中的手机号和验证码是否一致
        conn = get_redis_connection()
        redis_code = conn.get(mobile_phone)
        if not redis_code:
            raise ValidationError('验证码失效或未发送，请重新发送')
        # redis中的code是byts类型 需要转换后判断
        redis_srt_code = redis_code.decode('utf-8')
        if code.strip() != redis_srt_code:
            raise ValidationError('验证码错误，请重新输入')

        return code


class LoginFrom(BootStrapForm, forms.Form):
    """ 用户名登录 """
    username = forms.CharField(label='用户名', widget=forms.TextInput())
    password = forms.CharField(label='密码', widget=forms.PasswordInput())
    code = forms.CharField(label='图片验证码', widget=forms.TextInput())
