"""starkproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from app01 import models as m1
from app02 import models as m2
from django.shortcuts import HttpResponse
from app01 import views
from stark.service.stark import site


def index(request):
    print(m1.UserInfo._meta.app_label)
    print(m1.UserInfo._meta.model_name)

    print(m2.Role._meta.app_label)
    print(m2.Role._meta.model_name)
    return HttpResponse("hello")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', index),
    path('stark/', site.urls),
    path('test/', views.test),
]


# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('index/', index),
#     path('rbac/', ([
#                     path('login/', views.login),
#                     path('logout/', views.logout),
#                    ], None, "rbac")),
# ]
