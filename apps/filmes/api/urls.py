# apps/filmes/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.filmes.api.views import (
    FilmeViewSet,
    FilmesComSessoesView,
    GenerosFilmesView,
    FilmesPorGeneroView,
    FilmesPorCinemaView
)

router = DefaultRouter()
router.register('filmes', FilmeViewSet)

app_name = 'api_filmes'

urlpatterns = [
    # URLs do router (CRUD completo)
    path('', include(router.urls)),
    
    # URLs personalizadas
    path('filmes-com-sessoes/', 
         FilmesComSessoesView.as_view(), 
         name='filmes-com-sessoes'),
    
    path('generos/', 
         GenerosFilmesView.as_view(), 
         name='generos-filmes'),
    
    path('genero/<str:genero>/', 
         FilmesPorGeneroView.as_view(), 
         name='filmes-por-genero'),
    
    path('cinema/<int:cinema_id>/', 
         FilmesPorCinemaView.as_view(), 
         name='filmes-por-cinema'),
]
