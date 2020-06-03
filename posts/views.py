from django.shortcuts import render
from .models import Post
from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404


def index(request):
    latest = Post.objects.all()[:11]
    return render(request, 'index.html', {'posts': latest})


def group_posts(request, slug):
    latest = Post.objects.all().select_related('group').filter(
        group__slug=slug)[:12]
    if latest:
        group = latest[0].group
        return render(request, 'group.html', {'group': group, 'posts': latest})
    else:
        return HttpResponseNotFound(request)
