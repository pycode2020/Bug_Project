"""中间件"""
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from web import models
from django.conf import settings
import datetime


class Project(object):
    def __init__(self):
        self.user = None
        self.price_policy = None
        self.project = None


class AuthMiddleware(MiddlewareMixin):

    def process_request(self, request):
        """
        如果用户已登录，在request中赋值
        """
        request.project = Project()

        user_id = request.session.get('user_id', 0)
        user_object = models.UserInfo.objects.filter(id=user_id).first()

        request.project.user = user_object

        # 添加白名单：没有登录都可以访问 ; settings.py
        '''
        1.获取当前用户访问的url ；request.path_info
        2.检查url是否在白名单中，如果在就可以继续访问，如果不在则进行判断是否已登录
        '''
        if request.path_info in settings.WHITE_REGEX_URL_LIST:
            return
        # 检查用户是否已登录，已登录继续往后走，未登录则返回登录页面
        if not request.project.user:
            return redirect('login')

        # 登录成功后，获取当前用户的额度
        # 方式一：免费的额度在交易记录中存储
        # 获取当前用户，交易记录ID值最大的，已支付的值 （最近的交易记录）
        _object = models.Transaction.objects.filter(user=user_object, status=2).order_by('-id').first()

        # 判断是否支付状态是否过期
        current_datetime = datetime.datetime.now()
        if _object.end_datetime and _object.end_datetime < current_datetime:
            # 过期
            # _object = models.Transaction.objects.filter(user=user_object, status=2).order_by('id').first()
            _object = models.Transaction.objects.filter(user=user_object, status=2, price_policy__category=1).first()

        request.project.price_policy = _object.price_policy

        '''
                # 方式二：免费的额度存储配置文件
        # 获取当前用户，交易记录ID值最大的，已支付的值 （最近的交易记录）
        _object = models.Transaction.objects.filter(user=user_object, status=2).order_by('-id').first()
        if not _object:
            # 没有购买，免费版
            request.price_policy = models.PricePolicy.objects.filter(category=1, title='个人免费版').first()
        else:
            # 判断是否支付状态是否过期
            current_datetime = datetime.datetime.now()
            if _object.end_datetime and _object.end_datetime < current_datetime:
                # 过期
                request.price_policy = models.PricePolicy.objects.filter(category=1, title='个人免费版').first()
            else:
                request.price_policy = _object.price_policy
        '''

    def process_view(self, request, view, args, kwargs):
        # 判断URL是否是以manage开头，如果是则判断项目ID是否是我创建OR我参与的
        if not request.path_info.startswith('/manage/'):
            return

        # project_id必须是我创建或参与的
        project_id = kwargs.get('project_id')
        # 是否为我创建的
        project_object = models.Project.objects.filter(creator=request.project.user, id=project_id).first()
        if project_object:
            # 如果是我创建的项目，通过
            request.project.project = project_object
            return
        # 是否是我参与的项目
        project_user_object = models.ProjectUser.objects.filter(user=request.project.user,
                                                                project_id=project_id).first()
        if project_user_object:
            # 是我参与的项目
            request.project.project = project_user_object.project
            return

        return redirect('project_list')
