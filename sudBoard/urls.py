"""sudBoard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from bokeh.server.django import autoload
from django.contrib import admin
from django.urls import path,re_path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from vizApps.services import BoardService, VizService

from vizApps.controllers import BoardController

app_name = 'vizApps'

urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'board/<slug:slug>/', BoardController.getBoardFromSlug),
    path(r'board/<slug:boardSlug>/vizentity/<slug:vizSlug>', BoardController.getBoardVizElementFromSlug),
]

bokeh_apps = [
    autoload(f"^board/(?P<slug>[-a-zA-Z0-9_]+)/", BoardService.getApp),
    autoload(f"^board/(?P<slug>[-a-zA-Z0-9_]+)/vizentity/(?P<url>[-a-zA-Z0-9_]+)", VizService.getApp),
]

urlpatterns += staticfiles_urlpatterns()
