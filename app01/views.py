from django.shortcuts import render, HttpResponse
import random


# Create your views here.


def send_sms(request):
    """模拟短信发送功能"""
    code = random.randrange(1000, 9999)
    print(code)
    return HttpResponse(code)


from django import forms
from app01 import models
from django.core.validators import RegexValidator  # 正则模块
from django.core.exceptions import ValidationError  # 正则模块


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


def register(request):
    """注册功能"""
    form = RegisterModelForm()
    return render(request, 'app01/register.html', {'form': form})


if __name__ == '__main__':
    # send_sms(1)
    ...
