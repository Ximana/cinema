#apps/core/urls.py
from django.urls import path
from . import views

app_name = 'cinemas'

urlpatterns = [

    path('', views.CinemaListView.as_view(), name='lista'),
    path('<int:pk>/', views.CinemaDetailView.as_view(), name='detalhes'), 
    path('editar/<int:pk>/', views.CinemaUpdateView.as_view(), name='editar'),
    path('remover/<int:pk>/', views.CinemaDeleteView.as_view(), name='remover'),

    
    
]

