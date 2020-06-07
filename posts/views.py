from django.shortcuts import render, redirect
from .models import Post
from django.http import HttpResponseNotFound
from .forms import PostForm


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


def new_post(request):
    form = PostForm(request.POST or request.GET)
    if request.method == 'POST' and form.is_valid():
        new = form.save(commit=False)
        new.author_id = request.user.id
        new.save()
        return redirect('index')
    return render(request, 'new.html', {'form': form})
