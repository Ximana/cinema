# apps/filmes/api/views.py
from rest_framework import viewsets, permissions, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db.models import Q, Count, F, Exists, OuterRef

from apps.filmes.models import Filme
from apps.sessoes.models import Sessao
from apps.cinemas.models import Cinema

from apps.filmes.serializers import (
    FilmeListSerializer,
    FilmeDetailSerializer,
    FilmeCreateUpdateSerializer,
    FilmeComSessoesSerializer
)


class FilmeViewSet(viewsets.ModelViewSet):
    """ViewSet para operações CRUD de filmes"""
    queryset = Filme.objects.filter(
        sessoes__horario__gte=timezone.now()
    ).distinct().order_by('-data_lancamento')
    
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['titulo', 'diretor', 'genero', 'sinopse']
    ordering_fields = ['titulo', 'data_lancamento', 'data_registo']
    ordering = ['-data_lancamento']
    
    def get_queryset(self):
        """Retornar apenas filmes com sessões disponíveis"""
        return Filme.objects.filter(
            sessoes__horario__gte=timezone.now()
        ).distinct().order_by('-data_lancamento')
    
    def get_serializer_class(self):
        """Retornar serializer adequado para cada action"""
        if self.action == 'retrieve':
            return FilmeDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return FilmeCreateUpdateSerializer
        return FilmeListSerializer
    
    def get_permissions(self):
        """Permissões personalizadas para diferentes ações"""
        if self.action in ['list', 'retrieve']:
            # Qualquer pessoa pode ver os filmes
            return [permissions.AllowAny()]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Apenas administradores podem gerenciar filmes
            return [permissions.IsAdminUser()]
        return super().get_permissions()
    
    @action(detail=False, methods=['get'], url_path='por-genero/(?P<genero>[^/.]+)')
    def por_genero(self, request, genero=None):
        """Listar filmes por gênero (apenas com sessões disponíveis)"""
        filmes = self.get_queryset().filter(genero__iexact=genero)
        
        page = self.paginate_queryset(filmes)
        if page is not None:
            serializer = FilmeListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = FilmeListSerializer(filmes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def sessoes(self, request, pk=None):
        """Ver detalhes do filme com todas as suas sessões disponíveis"""
        try:
            filme = self.get_object()
            serializer = FilmeComSessoesSerializer(filme)
            return Response(serializer.data)
        except Filme.DoesNotExist:
            return Response(
                {'erro': 'Filme não encontrado.'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'], url_path='por-cinema/(?P<cinema_id>\d+)')
    def por_cinema(self, request, cinema_id=None):
        """Listar filmes com sessões disponíveis em um cinema específico"""
        try:
            cinema = Cinema.objects.get(id=cinema_id)
        except Cinema.DoesNotExist:
            return Response(
                {'erro': 'Cinema não encontrado.'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        filmes = self.get_queryset().filter(
            sessoes__sala__cinema=cinema
        ).distinct()
        
        page = self.paginate_queryset(filmes)
        if page is not None:
            serializer = FilmeListSerializer(page, many=True, context={'cinema_id': cinema_id})
            return self.get_paginated_response(serializer.data)
        
        serializer = FilmeListSerializer(filmes, many=True, context={'cinema_id': cinema_id})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def em_cartaz(self, request):
        """Listar filmes atualmente em cartaz (com sessões hoje)"""
        hoje = timezone.now().date()
        filmes = self.get_queryset().filter(
            sessoes__horario__date=hoje
        ).distinct()
        
        page = self.paginate_queryset(filmes)
        if page is not None:
            serializer = FilmeListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = FilmeListSerializer(filmes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def proximos_lancamentos(self, request):
        """Listar filmes com sessões nos próximos dias"""
        dias = int(request.query_params.get('dias', 7))
        data_limite = timezone.now() + timezone.timedelta(days=dias)
        
        filmes = self.get_queryset().filter(
            sessoes__horario__gte=timezone.now(),
            sessoes__horario__lte=data_limite
        ).distinct()
        
        page = self.paginate_queryset(filmes)
        if page is not None:
            serializer = FilmeListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = FilmeListSerializer(filmes, many=True)
        return Response(serializer.data)


class FilmesComSessoesView(generics.ListAPIView):
    """View para listar apenas filmes que têm sessões disponíveis"""
    serializer_class = FilmeListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['titulo', 'diretor', 'genero']
    ordering_fields = ['titulo', 'data_lancamento']
    ordering = ['-data_lancamento']
    
    def get_queryset(self):
        """Retornar apenas filmes com sessões futuras"""
        return Filme.objects.filter(
            sessoes__horario__gte=timezone.now()
        ).distinct().order_by('-data_lancamento')


class GenerosFilmesView(generics.ListAPIView):
    """View para listar gêneros de filmes com sessões disponíveis"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, *args, **kwargs):
        """Retornar lista de gêneros de filmes com sessões disponíveis"""
        generos = Filme.objects.filter(
            sessoes__horario__gte=timezone.now()
        ).values_list('genero', flat=True).distinct().order_by('genero')
        
        return Response({
            'generos': list(generos)
        })


class FilmesPorGeneroView(generics.ListAPIView):
    """View para listar filmes de um gênero específico"""
    serializer_class = FilmeListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [OrderingFilter]
    ordering_fields = ['titulo', 'data_lancamento']
    ordering = ['-data_lancamento']
    
    def get_queryset(self):
        """Filtrar filmes por gênero (apenas com sessões disponíveis)"""
        genero = self.kwargs.get('genero')
        return Filme.objects.filter(
            genero__iexact=genero,
            sessoes__horario__gte=timezone.now()
        ).distinct().order_by('-data_lancamento')


class FilmesPorCinemaView(generics.ListAPIView):
    """View para listar filmes disponíveis em um cinema específico"""
    serializer_class = FilmeListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['titulo', 'diretor', 'genero']
    ordering_fields = ['titulo', 'data_lancamento']
    ordering = ['-data_lancamento']
    
    def get_queryset(self):
        """Filtrar filmes por cinema (apenas com sessões disponíveis)"""
        cinema_id = self.kwargs.get('cinema_id')
        return Filme.objects.filter(
            sessoes__sala__cinema_id=cinema_id,
            sessoes__horario__gte=timezone.now()
        ).distinct().order_by('-data_lancamento')
    
    def get_serializer_context(self):
        """Adicionar cinema_id ao contexto do serializer"""
        context = super().get_serializer_context()
        context['cinema_id'] = self.kwargs.get('cinema_id')
        return context
