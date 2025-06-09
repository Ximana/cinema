#apps/core/urls.py
from django.urls import path
from . import views
from django.shortcuts import render

app_name = 'usuarios'

urlpatterns = [
    
    # Usuarios
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('usuarios/lista/', views.UsuarioListView.as_view(), name='lista'),
    path('usuarios/detalhe/<int:pk>/', views.UsuarioDetailView.as_view(), name='detalhes'),
    path('usuarios/remover/<int:pk>/', views.UsuarioDeleteView.as_view(), name='remover'),
    path('usuarios/atualizar/', views.UsuarioUpdateView.as_view(), name='atualizar'),    
    path('usuario/foto/atualizar/', views.AtualizarFotoView.as_view(), name='atualizar_foto'),
    path('usuario/senha/alterar/', views.AlterarSenhaView.as_view(), name='alterar_senha'), 
    
]