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


class PostEditor:

    def __init__(self, request, author: str = '', post_id: int = 0):
        self.redirect_to = None
        self._form = None
        self._post = None
        self._request = request
        if not self._request.user.is_authenticated:
            self.redirect_to = reverse('login')
            return
        if author and post_id:
            self._mode = 'edit'
            if request.user.username != author:
                try:
                    self._post = Post.objects.get(
                        author__username=author, pk=post_id)
                except Post.DoesNotExist:
                    pass
                if self._post:
                    self.redirect_to = reverse(
                        'post', kwargs={'post_id': self._post.id,
                                        'username': self._post.author})
                else:
                    self.redirect_to = reverse('index')
                return
            self._author = get_object_or_404(User, username=author)
            self._post_id = post_id
        else:
            self._mode = 'create'
            self._author = request.user
            self._post_id = 0

    def render(self):
        if self.redirect_to:
            return redirect(self.redirect_to)

        if self._mode == 'create':
            self._set_post_and_form_on_create()
        else:
            self._set_post_and_form_on_edit()
        res = self._render()

        if self.redirect_to:
            res = redirect(self.redirect_to)

        return res

    def _render(self):
        if self._request.method == 'GET':
            return self._render_on_get()
        else:
            return self._render_on_post()

    def _render_on_post(self):
        if self._form.is_valid():
            self._post.save()
            if self._mode == 'edit':
                self.redirect_to = reverse(
                    'post', kwargs={'username': self._post.author.username,
                                    'post_id': self._post.id}
                )
            else:
                # не понял, зачем в тестах требование перенаправления на
                # главную страницу - логичнее было бы перенаправлять на
                # страницу поста
                self.redirect_to = reverse('index')
        else:
            print_form_errors(PostForm(data=self._request.POST))
            return self._render_on_get()

    def _render_on_get(self):
        context = {
            'form': self._form,
            'create_or_edit': self._mode == 'create',
            'post': self._post
        }
        if self._mode == 'edit':
            context['post_id'] = str(self._post.id)
        return render(self._request, 'post_edit.html', context)

    def _set_post_and_form_on_create(self):
        self._form = PostForm(self._request.POST or None)
        self._post = self._form.save(commit=False)
        self._post.author = self._request.user

    def _set_post_and_form_on_edit(self):
        self._post = Post.objects.get(
            author__username=self._request.user.username, id=self._post_id)
        if self._request.method == 'GET':
            self._form = PostForm(instance=self._post)
        else:
            self._form = PostForm(self._request.POST, instance=self._post)


def post_new(request):
    editor = PostEditor(request)
    return editor.render()


def post_edit(request, username=None, post_id=0):
    editor = PostEditor(request, username, post_id)
    return editor.render()
