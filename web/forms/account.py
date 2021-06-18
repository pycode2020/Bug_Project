"""
vimes.account.py 调用的form
"""

from django import forms
from web import models
from django.core.validators import RegexValidator  # 正则模块
from django.core.exceptions import ValidationError
from django_redis import get_redis_connection
import random,redis


class RegisterModelForm(forms.ModelForm):
    """ModelForm生成注册页面表单字段"""
    # 对手机号码字段类型重写，进行正则判断
    mobile_phone = forms.CharField(label='手机号码', validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', '手机号格式错误'), ])
    # 对密码字段类型重写，密码插件，展示时为密文
    password = forms.CharField(label='密码', widget=forms.PasswordInput())
    # 重复确认密码； attrs={,}属性可以添加class类样式
    confirm_password = forms.CharField(label='确认密码', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': '确认密码'}))
    # 验证码; attrs={,}属性可以添加class类样式
    # code = forms.CharField(label='验证码', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '验证码'}))
    code = forms.CharField(label='验证码', widget=forms.TextInput(attrs={'placeholder': '验证码'}))

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

        # 校验数据库中是否存在这个手机号码
        exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        # 如果存在，返回以下异常
        if exists:
            raise ValidationError('手机号码已存在')

        # 发短信 & 写入redis
        # 随机生成验证码
        code = random.randrange(1000, 9999)
        print(code)

        # 验证码写入redis(django-redis)
        conn = get_redis_connection()  # 连接redis
        # conn = redis.Redis(host='127.0.0.1', port=6379, encoding='utf-8')
        conn.set(mobile_phone, code, ex=60)  # 超时时间为60s

        return mobile_phone
    # def __init__(self, request, *args, **kwargs):
    #     """将 views.py.send_sms的request传过来"""
    #     super.__init__(*args, **kwargs)
    #     self.request = request
    #
    # def clean_mobile_phone(self):
    #     """手机号码构验的钩子"""
    #     # 用户提交的手机号码
    #     mobile_phone = self.cleaned_data['mobile_phone']
    #
    #     # 判断模板是否有问题
    #     tpl = self.request.GET.get('tpl')  # 短信的模板：register or login
    #     template_id = settings.TENCENT_SMS_TEMPLATE.get(tpl)  # 找到settings.py中对应的短信模板id
    #     if not template_id:
    #         raise ValidationError('模板错误')
    #
    #     # 校验数据库中是否存在这个手机号码
    #     exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
    #     # 如果存在，返回以下异常
    #     if exists:
    #         raise ValidationError('手机号码已存在')
    #
    #     # 发短信 & 写入redis
    #     code = random.randrange(1000, 9999)
    #     self.code = code
    #     print(code)
    #
    #     # 验证码写入redis(django-redis)
    #     conn = get_redis_connection()  # 连接redis
    #     conn.set(mobile_phone, code, ex=60)  # 超时时间为60s
    #
    #     return mobile_phone
