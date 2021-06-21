import os
import sys
import django

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Bug_Project.settings')
django.setup()  # 模拟启动

from web import models

# 往数据库添加数据：连接数据库，操作，关闭链接。
models.UserInfo.objects.create(
    username='zhangsan',
    email='zhangsan@1.com',
    mobile_phone='13000000000',
    password='123456',
)
