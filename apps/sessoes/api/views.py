# apps/sessoes/api/views.py
from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db.models import Q, Count, F

from apps.cinemas.models import Cinema
from apps.sessoes.models import Sessao

from apps.sessoes.serializers import (
    SessaoListSerializer,
    SessaoDetailSerializer,
    SessaoCreateUpdateSerializer
)

class SessaoViewSet(viewsets.ModelViewSet):
    """ViewSet para operações CRUD de sessões"""
    queryset = Sessao.objects.select_related(
        'filme', 'sala', 'sala__cinema'
    ).filter(horario__gte=timezone.now()).order_by('horario')
    
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['filme__titulo', 'sala__cinema__nome', 'sala__cinema__localizacao']
    ordering_fields = ['horario', 'preco_base']
    ordering = ['horario']
    
    def get_queryset(self):
        """Aplicar filtros manuais"""
        queryset = super().get_queryset()
        
        # Filtros manuais
        genero = self.request.query_params.get('genero')
        cinema_id = self.request.query_params.get('cinema')
        tipo = self.request.query_params.get('tipo')
        idioma = self.request.query_params.get('idioma')
        data_inicio = self.request.query_params.get('data_inicio')
        data_fim = self.request.query_params.get('data_fim')
        preco_min = self.request.query_params.get('preco_min')
        preco_max = self.request.query_params.get('preco_max')
        
        if genero:
            queryset = queryset.filter(filme__genero__icontains=genero)
        
        if cinema_id:
            queryset = queryset.filter(sala__cinema_id=cinema_id)
        
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        if idioma:
            queryset = queryset.filter(idioma=idioma)
        
        if data_inicio:
            queryset = queryset.filter(horario__date__gte=data_inicio)
        
        if data_fim:
            queryset = queryset.filter(horario__date__lte=data_fim)
        
        if preco_min:
            queryset = queryset.filter(preco_base__gte=preco_min)
        
        if preco_max:
            queryset = queryset.filter(preco_base__lte=preco_max)
        
        return queryset
    
    def get_serializer_class(self):
        """Retornar serializer adequado para cada action"""
        if self.action == 'retrieve':
            return SessaoDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return SessaoCreateUpdateSerializer
        return SessaoListSerializer
    
    def get_permissions(self):
        """Permissões personalizadas para diferentes ações"""
        if self.action in ['list', 'retrieve']:
            # Qualquer pessoa pode ver as sessões
            return [permissions.AllowAny()]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Apenas administradores podem gerenciar sessões
            return [permissions.IsAdminUser()]
        return super().get_permissions()
    
    @action(detail=False, methods=['get'], url_path='por-genero/(?P<genero>[^/.]+)')
    def por_genero(self, request, genero=None):
        """Listar sessões por gênero de filme"""
        sessoes = self.get_queryset().filter(filme__genero__iexact=genero)
        
        page = self.paginate_queryset(sessoes)
        if page is not None:
            serializer = SessaoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = SessaoListSerializer(sessoes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='por-cinema/(?P<cinema_id>\d+)')
    def por_cinema(self, request, cinema_id=None):
        """Listar sessões por cinema específico"""
        try:
            cinema = Cinema.objects.get(id=cinema_id)
        except Cinema.DoesNotExist:
            return Response(
                {'erro': 'Cinema não encontrado.'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        sessoes = self.get_queryset().filter(sala__cinema=cinema)
        
        page = self.paginate_queryset(sessoes)
        if page is not None:
            serializer = SessaoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = SessaoListSerializer(sessoes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def hoje(self, request):
        """Listar sessões de hoje"""
        hoje = timezone.now().date()
        sessoes = self.get_queryset().filter(horario__date=hoje)
        
        page = self.paginate_queryset(sessoes)
        if page is not None:
            serializer = SessaoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = SessaoListSerializer(sessoes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def proximos_dias(self, request):
        """Listar sessões dos próximos 7 dias"""
        dias = int(request.query_params.get('dias', 7))
        data_limite = timezone.now() + timezone.timedelta(days=dias)
        
        sessoes = self.get_queryset().filter(
            horario__gte=timezone.now(),
            horario__lte=data_limite
        )
        
        page = self.paginate_queryset(sessoes)
        if page is not None:
            serializer = SessaoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = SessaoListSerializer(sessoes, many=True)
        return Response(serializer.data)

class SessoesPorFilmeView(generics.ListAPIView):
    """View para listar sessões de um filme específico"""
    serializer_class = SessaoListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [OrderingFilter]
    ordering_fields = ['horario', 'preco_base']
    ordering = ['horario']
    
    def get_queryset(self):
        """Filtrar sessões por filme"""
        filme_id = self.kwargs.get('filme_id')
        return Sessao.objects.select_related(
            'filme', 'sala', 'sala__cinema'
        ).filter(
            filme_id=filme_id,
            horario__gte=timezone.now()
        ).order_by('horario')

class SessoesDisponiveisView(generics.ListAPIView):
    """View para listar apenas sessões com assentos disponíveis"""
    serializer_class = SessaoListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['filme__titulo', 'sala__cinema__nome']
    ordering_fields = ['horario', 'preco_base']
    ordering = ['horario']
    
    def get_queryset(self):
        """Retornar apenas sessões com assentos disponíveis"""
        try:
            from apps.reservas.models import Ingresso
            
            return Sessao.objects.select_related(
                'filme', 'sala', 'sala__cinema'
            ).annotate(
                ingressos_vendidos=Count('reservas__ingressos', 
                                       filter=Q(reservas__ingressos__status__in=['emitido', 'utilizado']))
            ).filter(
                horario__gte=timezone.now(),
                ingressos_vendidos__lt=F('sala__capacidade')
            ).order_by('horario')
        except:
            # Se não existir o modelo Ingresso ainda, retorna todas as sessões
            return Sessao.objects.select_related(
                'filme', 'sala', 'sala__cinema'
            ).filter(horario__gte=timezone.now()).order_by('horario')

class GenerosSessoesView(generics.ListAPIView):
    """View para listar gêneros de filmes com sessões disponíveis"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, *args, **kwargs):
        """Retornar lista de gêneros com sessões disponíveis"""
        generos = Sessao.objects.filter(
            horario__gte=timezone.now()
        ).values_list('filme__genero', flat=True).distinct().order_by('filme__genero')
        
        return Response({
            'generos': list(generos)
        })

class CinemasSessoesView(generics.ListAPIView):
    """View para listar cinemas com sessões disponíveis"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, *args, **kwargs):
        """Retornar lista de cinemas com sessões disponíveis"""
        from apps.sessoes.serializers import CinemaSerializer
        
        cinemas = Cinema.objects.filter(
            salas__sessoes__horario__gte=timezone.now()
        ).distinct().order_by('nome')
        
        serializer = CinemaSerializer(cinemas, many=True)
        return Response(serializer.data)