#apps/core/urls.py
from django.urls import path
from . import views
#from django.shortcuts import render

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
]