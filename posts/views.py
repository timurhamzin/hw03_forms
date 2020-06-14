from django.shortcuts import render, redirect, get_object_or_404
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


class PostEditor:

    def __init__(self, username: str, post_id: int, author: User, request):
        self._author = author
        self._username = username
        self._post_id = post_id
        if post_id is None:
            self.mode = 'create'
        else:
            self.mode = 'edit'
        self._request = request

    def render_on_create(self):
        form = PostForm(self._request.POST or None)
        post = form.save(commit=False)

    def render(self):
        if self._mode == 'create':
            # post is being created
            form = PostForm(self._request.POST or None)
            post = form.save(commit=False)
        else:
            # post is being edited
            if self._request.method == 'GET':
                print(f'Print: getting post by id {post_id}')
                post = Post.objects.get(author__username=author, id=post_id)
                form = PostForm(instance=post)
            else:
                form = PostForm(self._request.POST)
        if self._request.method == 'POST':
            if form.is_valid():
                print(
                    f'Print: form is valid, posting post {post_id}')
                if self._mode == 'create':
                    post = form.save(commit=False)
                    post.author = self._request.user
                else:
                    post = Post.objects.get(author__username=author, id=post_id)
                    post.text = self._request.POST.get('text')
                    post.group = Group.objects.get(id=int(self._request.POST.get('group')))
                post.save()
                print(f'Print: showing post_view of post by id {post.id}')
            else:
                print(
                    f'Print: form is NOT valid for post {post_id}')
            return post_view(self._request, post.author, post.id)
        else:
            # showing GET-self._request results
            print(f'Print: showing GET-request results for post {post_id}')
            print(f'Print: create_or_edit={self._mode}')
            print(f'Print: post_id={post_id}')
            print(f'Print: username={username}')
            return render(self._request, 'post_edit.html',
                          {'form': form, 'create_or_edit': self._mode == 'create',
                           'post_id': str(post_id), 'username': username,
                           'post': post})

def create_or_edit_post(request, username: str = None, post_id: int = None):
    if username is not None:
        author = get_object_or_404(User, username=username)
    else:
        author = request.user
    mode = post_id is None
    if request.user == author:
        post_editor = PostEditor(username, post_id, author, request)
        return post_editor.render()
    else:
        raise PermissionError(f'Unauthorised access: {request.user} '
                              f'trying to edit {author}`s post')


def post_new(request):
    return create_or_edit_post(request)


def post_edit(request, username, post_id):
    return create_or_edit_post(request, username, post_id)
