# apps/reservas/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.reservas.api.views import (
    MinhasReservasViewSet,
    MeusIngressosViewSet
)

router = DefaultRouter()
router.register('minhas-reservas', MinhasReservasViewSet, basename='minhas-reservas')
router.register('meus-ingressos', MeusIngressosViewSet, basename='meus-ingressos')

app_name = 'api_reservas'

urlpatterns = [
    path('', include(router.urls)),
]