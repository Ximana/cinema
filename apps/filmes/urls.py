#apps/core/urls.py
from django.urls import path
from . import views
from django.shortcuts import render

app_name = 'filmes'

urlpatterns = [
    
    path('filmes/listaFilmes/', views.FilmeListView.as_view(), name='lista'),
    path('filmes/detalhe/<int:pk>/', views.FilmeDetailView.as_view(), name='detalhes'), 
    path('filmes/editar/<int:pk>/', views.FilmeUpdateView.as_view(), name='editar'),
    path('filmes/remover/<int:pk>/', views.FilmeDeleteView.as_view(), name='remover'),

    
]