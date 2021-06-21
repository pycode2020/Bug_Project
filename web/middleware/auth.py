"""中间件"""

from django.utils.deprecation import MiddlewareMixin
from web import models


class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        """
        如果用户已登录，在request中赋值
        """
        user_id = request.session.get('user_id', 0)
        user_object = models.UserInfo.objects.filter(id=user_id).first()
        request.project = user_object  # .project是定义的项目名称
