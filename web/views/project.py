from django.shortcuts import render, HttpResponse, redirect
from web.forms.project import ProjectModelForm
from django.http import JsonResponse
from web import models


def project_list(request):
    """项目列表"""
    if request.method == 'GET':
        # GET查看项目列表
        '''
        思路：
        1.从数据库中获取两部分数据
            我创建的所有项目：已星际，未星标
            我参与的所有项目：已星际，未星标
        2.提取已星标
            列表 = 循环 [我创建的所有项目] + [我参与的所有项目] 把已星标的数据提取	
        得到三个列表： 星标、创建、参与
        '''
        project_dict = {'star': [], 'my': [], 'join': []}

        my_project_list = models.Project.objects.filter(creator=request.project.user)
        for row in my_project_list:
            if row.star:
                project_dict['star'].append({'value': row, 'type': 'my'})
            else:
                project_dict['my'].append(row)

        join_project_list = models.ProjectUser.objects.filter(user=request.project.user)
        for item in join_project_list:
            if item.star:
                project_dict['star'].append({'value': item.project, 'type': 'join'})
            else:
                project_dict['join'].append(item.project)

        form = ProjectModelForm(request)
        return render(request, 'project_list.html', {'form': form, 'project_dict': project_dict})
    # POST，ajax添加项目
    form = ProjectModelForm(request, data=request.POST)
    if form.is_valid():
        # 验证通过：项目名，颜色，描述，+ 谁创建的项目
        form.instance.creator = request.project.user
        # 创建项目
        form.save()
        return JsonResponse({'status': True})

    return JsonResponse({'status': False, 'error': form.errors})


def project_star(request, project_type, project_id):
    """添加星标"""
    if project_type == 'my':
        models.Project.objects.filter(id=project_id, creator=request.project.user).update(star=True)
        return redirect('project_list')
    if project_type == 'join':
        models.ProjectUser.objects.filter(project_id=project_id, user=request.project.user).update(star=True)
        return redirect('project_list')

    return HttpResponse('请求错误')

def project_unstar(request, project_type, project_id):
    """ 取消星标"""
    if project_type == 'my':
        models.Project.objects.filter(id=project_id, creator=request.project.user).update(star=False)
        return redirect('project_list')
    if project_type == 'join':
        models.ProjectUser.objects.filter(project_id=project_id, user=request.project.user).update(star=False)
        return redirect('project_list')

    return HttpResponse('请求错误')

