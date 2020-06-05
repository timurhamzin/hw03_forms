from django.forms import ModelForm
from posts.models import Post
from django.utils.translation import gettext_lazy as _


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ("group", "text")
        labels = {
            'group': _('Group'),
            'text': _('Text'),
        }
