# urls.py - Reservas
from django.urls import path
from . import views

app_name = 'reservas'

urlpatterns = [
    path('', views.ReservaListView.as_view(), name='lista'),
    path('detalhes/<int:pk>/', views.reserva_detalhes_ajax, name='detalhes_ajax'),
]