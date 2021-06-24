from django.shortcuts import render


def wiki(request, project_id):
    """首页"""
    return render(request, 'wiki.html')
