"""yatube URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib import flatpages
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('about/', include('django.contrib.flatpages.urls')),
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
]

urlpatterns += [
    path('about-author/', flatpages.views.flatpage, {'url': '/about-author/'},
         name='about-author'),
    path('about-spec/', flatpages.views.flatpage, {'url': '/about-spec/'},
         name='about-spec'),
]

urlpatterns += [
    path('', include('posts.urls')),
]

urlpatterns += staticfiles_urlpatterns()

plans = [
    {
        "name": "Бесплатно",
        "price": "0",
        "options": {"users": 10, "space": 10, "support": "Почтовая рассылка"},
    },
    {
        "name": "Профессиональный",
        "price": "49",
        "options": {"users": 50, "space": 100, "support": "Телефон и email"},
    },
    {
        "name": "Корпоративный",
        "price": "99",
        "options": {"users": 100, "space": 500,
                    "support": "Персональный менеджер"},
    },
]
