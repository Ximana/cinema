# views.py
from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum
from .models import Sessao
from apps.reservas.models import Reserva, Ingresso
from django.views.generic import ListView
from django.db.models import Q
from django.utils import timezone

class SessaoListView(LoginRequiredMixin, ListView):
    model = Sessao
    template_name = 'sessoes/listarSessoes.html'
    context_object_name = 'sessoes'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Sessao.objects.select_related(
            'filme', 
            'sala__cinema'
        )
        
        # Filtro de busca
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(filme__titulo__icontains=search_query) |
                Q(sala__nome__icontains=search_query) |
                Q(sala__cinema__nome__icontains=search_query) |
                Q(pk__icontains=search_query)
            )
        
        # Filtro por tipo de sessão
        tipo_selecionado = self.request.GET.get('tipo')
        if tipo_selecionado:
            queryset = queryset.filter(tipo=tipo_selecionado)
        
        # Filtro por idioma
        idioma_selecionado = self.request.GET.get('idioma')
        if idioma_selecionado:
            queryset = queryset.filter(idioma=idioma_selecionado)
        
        # Filtro por período
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')
        if data_inicio:
            queryset = queryset.filter(horario__date__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(horario__date__lte=data_fim)
        
        return queryset.order_by('horario')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['tipo_selecionado'] = self.request.GET.get('tipo', '')
        context['idioma_selecionado'] = self.request.GET.get('idioma', '')
        context['data_inicio'] = self.request.GET.get('data_inicio', '')
        context['data_fim'] = self.request.GET.get('data_fim', '')
        context['tipo_choices'] = Sessao.TIPO_SESSAO_CHOICES
        context['idioma_choices'] = Sessao.TIPO_IDIOMA_CHOICES
        return context

class SessaoDetailView(LoginRequiredMixin, DetailView):
    model = Sessao
    template_name = 'sessoes/detalhes.html'
    context_object_name = 'sessao'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sessao = self.object
        
        # Obter todas as reservas da sessão
        reservas = Reserva.objects.filter(sessao=sessao).select_related('usuario')
        context['reservas'] = reservas
        
        # Estatísticas da sessão
        total_reservas = reservas.count()
        reservas_confirmadas = reservas.filter(status='confirmada').count()
        reservas_pendentes = reservas.filter(status='pendente').count()
        reservas_canceladas = reservas.filter(status='cancelada').count()
        
        # Total de ingressos vendidos
        ingressos_vendidos = Ingresso.objects.filter(
            reserva__sessao=sessao,
            status__in=['emitido', 'utilizado']
        ).count()
        
        # Capacidade disponível
        capacidade_total = sessao.sala.capacidade
        lugares_ocupados = ingressos_vendidos
        lugares_disponiveis = capacidade_total - lugares_ocupados
        
        # Receita total
        receita_total = reservas.filter(status='confirmada').aggregate(
            total=Sum('valor')
        )['total'] or 0
        
        # Adicionar ao contexto
        context.update({
            'total_reservas': total_reservas,
            'reservas_confirmadas': reservas_confirmadas,
            'reservas_pendentes': reservas_pendentes,
            'reservas_canceladas': reservas_canceladas,
            'ingressos_vendidos': ingressos_vendidos,
            'capacidade_total': capacidade_total,
            'lugares_ocupados': lugares_ocupados,
            'lugares_disponiveis': lugares_disponiveis,
            'percentual_ocupacao': (lugares_ocupados / capacidade_total * 100) if capacidade_total > 0 else 0,
            'receita_total': receita_total,
        })
        
        # Obter ingressos da sessão
        context['ingressos'] = Ingresso.objects.filter(
            reserva__sessao=sessao
        ).select_related('reserva__usuario').order_by('-data_emissao')
        
        return context

