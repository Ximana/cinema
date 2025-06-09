# apps/sessoes/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.sessoes.api.views import (
    SessaoViewSet,
    SessoesPorFilmeView,
    SessoesDisponiveisView,
    GenerosSessoesView,
    CinemasSessoesView
)

router = DefaultRouter()
router.register('sessoes', SessaoViewSet)

app_name = 'api_sessoes'

urlpatterns = [
    # URLs do router (CRUD completo)
    path('', include(router.urls)),
    
    # URLs personalizadas
    path('sessoes/filme/<int:filme_id>/', 
         SessoesPorFilmeView.as_view(), 
         name='sessoes-por-filme'),
    
    path('sessoes/disponiveis/', 
         SessoesDisponiveisView.as_view(), 
         name='sessoes-disponiveis'),
    
    path('generos/', 
         GenerosSessoesView.as_view(), 
         name='generos-disponiveis'),
    
    path('cinemas/', 
         CinemasSessoesView.as_view(), 
         name='cinemas-disponiveis'),
]