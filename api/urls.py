from django.urls import path, include

app_name = 'api'

urlpatterns = [
    path('usuarios/', include('apps.usuarios.api.urls', namespace='api_usuarios')),
    path('sessoes/', include('apps.sessoes.api.urls', namespace='api_sessoes')),
    path('filmes/', include('apps.filmes.api.urls', namespace='api_filmes')),
    # Aqui você pode adicionar outras APIs do projeto no futuro
]