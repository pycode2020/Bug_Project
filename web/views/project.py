from django.shortcuts import render, HttpResponse, redirect


def project_list(request):
    """项目列表"""


    return render(request, 'project_list.html')
