from . import views
from django.urls import path

app_name = 'sessoes'

urlpatterns = [
    # ... outras URLs existentes
    path('sessao/<int:pk>/', views.SessaoDetailView.as_view(), name='detalhes'),
    path('sessoes/', views.SessaoListView.as_view(), name='lista'),
]