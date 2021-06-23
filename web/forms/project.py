from django import forms
from django.core.exceptions import ValidationError
from web.forms.bootstrap import BootStrapForm
from web import models
from web.forms.widgets import ColorRadioSelect


class ProjectModelForm(BootStrapForm, forms.ModelForm):
    """ 新键项目forms表单"""

    # name = forms.CharField(label='名称')
    # desc  = forms.CharField(label='描述',widget=forms.Textarea())

    bootstrap_class_exclude = ['color']  # 去除color 默认的样式

    class Meta:
        model = models.Project
        fields = ['name', 'color', 'desc']
        # 重写样式或属性
        labels = {
            'name': '名称'
        }
        widgets = {
            'desc': forms.Textarea,
            'color': ColorRadioSelect(attrs={'class':'color-radio'}),
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_name(self):
        """  项目校验   """
        # 1. 当前用户创建的项目名称是否重复
        name = self.cleaned_data['name']
        exists = models.Project.objects.filter(name=name, creator=self.request.project.user).exists()
        if exists:
            raise ValidationError('项目名称已存在')
        # 2. 当前用户是否有额度创建项目
        # 最多创建项目数
        # self.request.project.price_policy.project_num
        # 已经创建项目数
        count = models.Project.objects.filter(creator=self.request.project.user).count()
        if count >= self.request.project.price_policy.project_num:
            raise ValidationError('项目个数超限，请购买套餐')
        return name
