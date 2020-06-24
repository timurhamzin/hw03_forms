from django.contrib.auth.models import User
from django.test.client import Client
from django.test import TestCase
from django.urls import reverse
from posts.models import Post


class TestStringMethods(TestCase):

    def test_length(self):
        self.assertEqual(len('yatube'), 6)

    def test_show_msg(self):
        self.assertTrue(True, msg="Важная проверка на истинность")


class TestUserProfile(TestCase):

    def __init__(self, *args, **kwargs):
        self._client = Client()
        self._user = None
        super().__init__(*args, **kwargs)

    def create_and_login_user(self):
        return self._create_user(login=True)

    def create_user(self):
        return self._create_user(login=False)

    def _create_user(self, login=True):
        password = 'my_password'
        self._user = User.objects._create_user('my_user', 'myemail@test.com',
                                               password)
        if login:
            self._client.login(username=self._user.username, password=password)
        return self._user

    def test_profile_created_for_new_user(self):
        self.create_and_login_user()
        response = self._client.get('/my_user/', follow=False)
        self.assertEqual(response.status_code, 200)

    def test_logged_user_can_publish_post_through_edit(self):
        self.create_and_login_user()
        response = self.publish_post_edit('test text')
        self.assertEqual(response.status_code, 200)

    def publish_post_edit(self, text):
        url = reverse('post_edit', args=[self._user.username, 0])
        response = self._client.post(url, data={'text': text}, follow=True)
        return response

    def test_logged_user_can_publish_post_through_new(self):
        self.create_and_login_user()
        response = self.publish_post_new('test text')
        self.assertEqual(response.status_code, 200)

    def publish_post_new(self, text):
        url = reverse('post_new')
        return self._client.post(url, data={'text': text}, follow=True)

    def test_unlogged_user_cannot_publish(self):
        self.create_user()
        url = reverse('post_new')
        response = self._client.post(url, data={'text': 'test text'},
                                     follow=False)
        redirects_to = reverse('login')
        self.assertRedirects(response, redirects_to)

    def test_published_post_found(self):
        self.create_and_login_user()
        post_text = 'test text'
        self.publish_post_new(post_text)

        self.post_is_found(post_text)

    def post_is_found(self, post_text):
        self.check_page_contains('index', post_text)

        url_kwargs = {'username': self._user.username}
        self.check_page_contains('profile', post_text, url_kwargs)

        post = Post.objects.get(author__username=self._user.username)
        url_kwargs = {'username': self._user.username, 'post_id': post.pk}
        self.check_page_contains('post', post_text, url_kwargs)

    def post_is_not_found(self, post_text):
        self.check_page_not_contains('index', post_text)

        url_kwargs = {'username': self._user.username}
        self.check_page_not_contains('profile', post_text, url_kwargs)

        post = Post.objects.get(author__username=self._user.username)
        url_kwargs = {'username': self._user.username, 'post_id': post.pk}
        self.check_page_not_contains('post', post_text, url_kwargs)

    def check_page_contains(self, url_name: str, contains: str,
                            url_kwargs: dict = None):
        url_with_post = reverse(url_name, kwargs=url_kwargs)
        response = self._client.get(url_with_post, follow=False)
        self.assertContains(response, contains)

    def check_page_not_contains(self, url_name: str, contains: str,
                                url_args: dict = None):
        url_with_post = reverse(url_name, kwargs=url_args)
        response = self._client.get(url_with_post, follow=False)
        self.assertNotContains(response, contains)

    def edit_post(self, post_pk, text):
        url = reverse('post_edit', args=[self._user.username, post_pk])
        response = self._client.post(url, data={'text': text}, follow=True)
        return response

    def test_logged_user_can_edit(self):
        self.create_and_login_user()
        post_text = 'test text'
        post_changed = 'changed post'
        self.publish_post_new(post_text)
        post = Post.objects.get(author__username=self._user.username)

        self.post_is_found(post_text)
        self.edit_post(post.pk, post_changed)
        self.post_is_not_found(post_text)
        self.post_is_found(post_changed)
