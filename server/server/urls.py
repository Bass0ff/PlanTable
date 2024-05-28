"""
URL configuration for server project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, re_path
from server_test import views

urlpatterns = [
    path(r'', views.empty, name='index'),
    path(r'auth', views.autho, name='authorisation'),
    path(r'reg', views.reg, name='registration'),
    path(r'getData', views.getData, name='collecting_data'),
    path(r'unData', views.unData, name='undoing_data'),
    path(r'upData', views.upData, name='updating_data'),
    path(r'docData', views.docData, name='generating_document'),
    path(r'tData', views.teachData, name='teacher_data'),
    path(r'tPass', views.teachPass, name='teacher_password'),
    path(r'unTeach', views.toggleTeach, name='toggling_teacher'),
    path(r'reTeach', views.upTeach, name='update_teacher')
]
