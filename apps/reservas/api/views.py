# apps/reservas/api/views.py
from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404

from apps.reservas.models import Reserva, Ingresso
from apps.reservas.serializers import (
    ReservaSerializer,
    CriarReservaSerializer,
    IngressoSerializer
)

class MinhasReservasViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar as reservas do usuário logado"""
    serializer_class = ReservaSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Retornar apenas as reservas do usuário logado"""
        return Reserva.objects.filter(
            usuario=self.request.user
        ).select_related(
            'sessao__filme',
            'sessao__sala__cinema'
        ).prefetch_related('ingressos').order_by('-data_hora_reserva')
    
    def get_serializer_class(self):
        """Usar serializer específico para criação"""
        if self.action == 'create':
            return CriarReservaSerializer
        return ReservaSerializer
    
    def create(self, request, *args, **kwargs):
        """Criar uma nova reserva"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reserva = serializer.save()
        
        # Retornar a reserva criada com o serializer padrão
        response_serializer = ReservaSerializer(reserva)
        return Response(
            {
                'mensagem': _('Reserva criada com sucesso!'),
                'reserva': response_serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    
    def retrieve(self, request, *args, **kwargs):
        """Visualizar detalhes de uma reserva específica"""
        return super().retrieve(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """Atualização não permitida - reservas não podem ser editadas"""
        return Response(
            {'erro': _('Reservas não podem ser editadas.')},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def partial_update(self, request, *args, **kwargs):
        """Atualização parcial não permitida - reservas não podem ser editadas"""
        return Response(
            {'erro': _('Reservas não podem ser editadas.')},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def destroy(self, request, *args, **kwargs):
        """Remover uma reserva (soft delete - cancelar)"""
        reserva = self.get_object()
        
        if reserva.status == 'cancelada':
            return Response(
                {'erro': _('Esta reserva já foi cancelada.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar se ainda é possível cancelar (ex: 2 horas antes da sessão)
        from django.utils import timezone
        from datetime import timedelta
        
        limite_cancelamento = reserva.sessao.horario - timedelta(hours=2)
        if timezone.now() > limite_cancelamento:
            return Response(
                {'erro': _('Não é possível cancelar esta reserva. Prazo expirado.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cancelar reserva e ingressos
        reserva.status = 'cancelada'
        reserva.save()
        
        # Cancelar todos os ingressos da reserva
        reserva.ingressos.update(status='cancelado')
        
        return Response(
            {'mensagem': _('Reserva cancelada com sucesso.')},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """Cancelar uma reserva específica"""
        reserva = self.get_object()
        
        if reserva.status == 'cancelada':
            return Response(
                {'erro': _('Esta reserva já foi cancelada.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar prazo de cancelamento
        from django.utils import timezone
        from datetime import timedelta
        
        limite_cancelamento = reserva.sessao.horario - timedelta(hours=2)
        if timezone.now() > limite_cancelamento:
            return Response(
                {'erro': _('Não é possível cancelar esta reserva. Prazo expirado.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cancelar reserva
        reserva.status = 'cancelada'
        reserva.save()
        
        # Cancelar ingressos
        reserva.ingressos.update(status='cancelado')
        
        return Response(
            {'mensagem': _('Reserva cancelada com sucesso.')},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def confirmar(self, request, pk=None):
        """Confirmar pagamento de uma reserva"""
        reserva = self.get_object()
        
        if reserva.status != 'pendente':
            return Response(
                {'erro': _('Apenas reservas pendentes podem ser confirmadas.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reserva.status = 'confirmada'
        reserva.save()
        
        return Response(
            {'mensagem': _('Reserva confirmada com sucesso.')},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def historico(self, request):
        """Listar histórico completo de reservas do usuário"""
        queryset = self.get_queryset()
        
        # Filtros opcionais
        status_filtro = request.query_params.get('status')
        if status_filtro:
            queryset = queryset.filter(status=status_filtro)
        
        # Paginação
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class MeusIngressosViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para visualizar ingressos do usuário"""
    serializer_class = IngressoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Retornar apenas ingressos do usuário logado"""
        return Ingresso.objects.filter(
            reserva__usuario=self.request.user
        ).select_related(
            'reserva__sessao__filme',
            'reserva__sessao__sala__cinema'
        ).order_by('-data_emissao')
    
    @action(detail=True, methods=['post'])
    def utilizar(self, request, pk=None):
        """Marcar um ingresso como utilizado"""
        ingresso = self.get_object()
        
        if ingresso.status != 'emitido':
            return Response(
                {'erro': _('Apenas ingressos emitidos podem ser utilizados.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar se é dia da sessão
        from django.utils import timezone
        if ingresso.reserva.sessao.horario.date() != timezone.now().date():
            return Response(
                {'erro': _('Este ingresso só pode ser utilizado no dia da sessão.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ingresso.status = 'utilizado'
        ingresso.save()
        
        return Response(
            {'mensagem': _('Ingresso utilizado com sucesso.')},
            status=status.HTTP_200_OK
        )
