from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('apps.core.urls')),
    path('usuarios/', include('apps.usuarios.urls')),
    path('cinemas/', include('apps.cinemas.urls')),
    path('filmes/', include('apps.filmes.urls')),
    path('sessoes/', include('apps.sessoes.urls')),
    path('reservas/', include('apps.reservas.urls')),
    
    # Incluindo as URLs da API
    path('api/', include('api.urls', namespace='api')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
