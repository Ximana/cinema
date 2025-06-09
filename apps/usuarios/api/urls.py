# apps/usuarios/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.usuarios.api.views import (
    UsuarioViewSet,
    RegistroUsuarioView,
    LoginUsuarioView,
    LogoutUsuarioView,
    MeuPerfilView,
    UploadFotoPerfilView
)

router = DefaultRouter()
router.register('usuarios', UsuarioViewSet)

app_name = 'api_usuarios'

urlpatterns = [
    path('', include(router.urls)),
    path('registro/', RegistroUsuarioView.as_view(), name='registro'),
    path('login/', LoginUsuarioView.as_view(), name='login'),
    path('logout/', LogoutUsuarioView.as_view(), name='logout'),
    path('meu-perfil/', MeuPerfilView.as_view(), name='meu-perfil'),
    path('upload-foto/', UploadFotoPerfilView.as_view(), name='upload-foto'),
]
