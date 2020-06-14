from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .models import Post, User, Group
from django.http import HttpResponseNotFound
from .forms import PostForm
from django.core.paginator import Paginator


def index(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    posts = Post.objects.all().select_related('group').filter(
        group__slug=slug)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)
    if posts:
        group = posts[0].group
        return render(request, 'group.html',
                      {'group': group, 'page': page, 'paginator': paginator})
    else:
        return HttpResponseNotFound(request)


def profile(request, username):
    posts = Post.objects.filter(author__username=username
                                ).select_related('author')
    if posts:
        paginator = Paginator(posts, 10)
        page_number = request.GET.get('page', 1)
        page = paginator.get_page(page_number)
        author = posts[0].author
        return render(request, 'profile.html',
                      {'author': author, 'posts': posts,
                       'page': page, 'paginator': paginator})
    else:
        return HttpResponseNotFound(request)


def post_view(request, username, post_id: int):
    post = Post.objects.get(author__username=username, id=post_id)
    posts_count = Post.objects.filter(author__username=username).count()
    if post:
        return render(request, 'post.html',
                      {'author': post.author, 'post': post,
                       'posts_count': posts_count})
    else:
        return HttpResponseNotFound(request)


def print_form_errors(form):
    for field in form.errors:
        print(form.errors[field].as_text())


class PostEditorRenderer:

    def __init__(self, post_id: int, author: User, request):
        self._author = author
        self._post_id = post_id
        if post_id is None:
            self._mode = 'create'
        else:
            self._mode = 'edit'
        self._request = request
        self._form = None
        self._post = None
        self._form_valid = False

    def render(self):
        if self._mode == 'create':
            self._create_post()
        else:
            self._edit_post()
        return self._render()

    def _create_post(self):
        self._form = PostForm(self._request.POST or None)
        if self._form.is_valid():
            self._post = self._form.save(commit=False)
            self._post.author = self._request.user
            self._post.save()
        self._form_valid = self._form.is_valid()

    def _edit_post(self):
        if self._request.method == 'GET':
            self._post = Post.objects.get(author__username=self._author.username, id=self._post_id)
            self._form = PostForm(instance=self._post)
        else:
            self._form = PostForm(self._request.POST)
            if self._form.is_valid():
                post = self._form.save(commit=False)
                post.author = self._request.user
                post.save()
        self._form_valid = self._form.is_valid()

    def _render(self):
        if self._request.method == 'GET':
            return self._render_on_get()
        else:
            return self._render_on_post()

    def _render_on_post(self):
        if self._form_valid:
            # return post_view(self._request, self._post.author, self._post.id)
            return redirect(reverse('post', kwargs={'username': self._author.username,
                                                    'post_id': self._post_id}))
        else:
            print(f'errors: {self._form.errors}')
            print_form_errors(self._form)
            return self._render_on_get()

    def _render_on_get(self):
        return render(self._request, 'post_edit.html',
                      {'form': self._form, 'create_or_edit': self._mode == 'create',
                       'post_id': str(self._post.id), 'username': self._author.username,
                       'post': self._post})


def create_or_edit_post(request, username: str = None, post_id: int = None):
    if username is not None:
        author = get_object_or_404(User, username=username)
    else:
        author = request.user
    if request.user == author:
        post_editor = PostEditorRenderer(post_id, author, request)
        return post_editor.render()
    else:
        raise PermissionError(f'Unauthorised access: {request.user} '
                              f'trying to edit {author}`s post')


def post_new(request):
    return create_or_edit_post(request)


def post_edit(request, username, post_id):
    return create_or_edit_post(request, username, post_id)
