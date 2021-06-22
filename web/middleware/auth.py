"""中间件"""
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from web import models
from django.conf import settings

class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        """
        如果用户已登录，在request中赋值
        """
        user_id = request.session.get('user_id', 0)
        user_object = models.UserInfo.objects.filter(id=user_id).first()
        request.project = user_object  # .project是定义的项目名称

        # 添加白名单：没有登录都可以访问 ; settings.py
        '''
        1.获取当前用户访问的url ；request.path_info
        2.检查url是否在白名单中，如果在就可以继续访问，如果不在则进行判断是否已登录
        '''
        if request.path_info in settings.WHITE_REGEX_URL_LIST:
            return
        # 检查用户是否已登录，已登录继续往后走，未登录则返回登录页面
        if not request.project:
            return redirect('login')

