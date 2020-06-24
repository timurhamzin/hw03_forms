from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Post, User
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
    author = User.objects.get(username=username)
    if author:
        posts = Post.objects.filter(author__username=author
                                    ).select_related('author')
        paginator = Paginator(posts, 10)
        page_number = request.GET.get('page', 1)
        page = paginator.get_page(page_number)
        return render(request, 'profile.html',
                      {'author': author, 'posts': posts,
                       'page': page, 'paginator': paginator})
    else:
        return HttpResponseNotFound(request)


def post_view(request, username: str, post_id: int):
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
        print(f'Field "{field}" error: {form.errors[field].as_text()}')


class PostEditorRenderer:

    def __init__(self, post_id: int, author: User, request):
        self._author = author
        self._post_id = post_id
        if post_id is None or post_id == 0:
            self._mode = 'create'
        else:
            self._mode = 'edit'
        self._request = request
        self._form = None
        self._post = None

    def render(self):
        if self._mode == 'create':
            if self._request.user.is_authenticated:
                self._create_post()
            else:  # user not logged in
                url = reverse('login')
                return redirect(url)
        else:
            self._edit_post()
        return self._render()

    def _create_post(self):
        self._form = PostForm(self._request.POST or None)
        self._post = self._form.save(commit=False)
        self._post.author = self._request.user

    def _edit_post(self):
        self._post = Post.objects.get(author__username=self._author.username,
                                      id=self._post_id)
        if self._request.method == 'GET':
            self._form = PostForm(instance=self._post)
        else:
            self._form = PostForm(self._request.POST, instance=self._post)
            if self._form.is_valid():
                post = self._form.save(commit=False)
                post.author = self._request.user

    def _render(self):
        if self._request.method == 'GET':
            return self._render_on_get()
        else:
            return self._render_on_post()

    def _render_on_post(self):
        if self._form.is_valid():
            self._post.save()
            kwargs = {'username': self._post.author.username,
                      'post_id': self._post.id}
            return redirect(reverse('post', kwargs=kwargs))
        else:
            print_form_errors(PostForm(data=self._request.POST))
            return self._render_on_get()

    def _render_on_get(self):
        context = {
            'form': self._form,
            'create_or_edit': self._mode == 'create',
            'username': self._author.username,
            'post': self._post
        }
        if self._mode == 'edit':
            context['post_id'] = str(self._post.id)
        return render(self._request, 'post_edit.html', context)


def create_or_edit_post(request, username: str = None, post_id: int = None):
    if username is not None:
        author = get_object_or_404(User, username=username)
    else:
        author = request.user
    if request.user == author:
        post_editor = PostEditorRenderer(post_id, author, request)
        return post_editor.render()
    else:
        return redirect(
            reverse('post', kwargs=dict(username=username, post_id=post_id)))


def post_new(request):
    response = create_or_edit_post(request)
    return response


def post_edit(request, username, post_id):
    response = create_or_edit_post(request, username, post_id)
    if response.status_code == 200:
        url = reverse('index')
        return redirect(url)
