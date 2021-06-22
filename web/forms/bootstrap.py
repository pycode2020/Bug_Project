class BootStrapForm(object):
    """ 让下面使用BootStrapForm的类继承这个基类"""

    # 重写__init__方法，添加上默认的class类 'form-control'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            # attrs={,}属性可以添加class类样式
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = '请输入%s' % (field.label,)
