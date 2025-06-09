# views.py - Reservas
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from .models import Reserva, Ingresso

class ReservaListView(LoginRequiredMixin, ListView):
    model = Reserva
    template_name = 'reservas/listarReservas.html'
    context_object_name = 'reservas'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Reserva.objects.select_related(
            'usuario', 
            'sessao__filme', 
            'sessao__sala__cinema'
        ).prefetch_related('ingressos')
        
        # Filtro de busca
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(usuario__first_name__icontains=search_query) |
                Q(usuario__last_name__icontains=search_query) |
                Q(usuario__email__icontains=search_query) |
                Q(sessao__filme__titulo__icontains=search_query) |
                Q(pk__icontains=search_query)
            )
        
        # Filtro por status
        status_selecionado = self.request.GET.get('status')
        if status_selecionado:
            queryset = queryset.filter(status=status_selecionado)
        
        # Filtro por período
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')
        if data_inicio:
            queryset = queryset.filter(data_hora_reserva__date__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(data_hora_reserva__date__lte=data_fim)
        
        return queryset.order_by('-data_hora_reserva')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['status_selecionado'] = self.request.GET.get('status', '')
        context['data_inicio'] = self.request.GET.get('data_inicio', '')
        context['data_fim'] = self.request.GET.get('data_fim', '')
        context['status_choices'] = Reserva.STATUS_CHOICES
        return context

def reserva_detalhes_ajax(request, pk):
    """View para retornar detalhes da reserva via AJAX"""
    reserva = get_object_or_404(Reserva.objects.select_related(
        'usuario', 
        'sessao__filme', 
        'sessao__sala__cinema'
    ).prefetch_related('ingressos'), pk=pk)
    
    # Preparar dados dos ingressos
    ingressos_data = []
    for ingresso in reserva.ingressos.all():
        ingressos_data.append({
            'numero': ingresso.numero,
            'preco': str(ingresso.preco),
            'status': ingresso.get_status_display(),
            'tipo_desconto': ingresso.get_tipo_desconto_display(),
            'assentos': ingresso.assentos,
            'data_emissao': ingresso.data_emissao.strftime('%d/%m/%Y %H:%M')
        })
    
    data = {
        'id': reserva.pk,
        'usuario': {
            'nome': reserva.usuario.get_nome_completo(),
            'email': reserva.usuario.email,
            'telefone': reserva.usuario.telefone or 'Não informado',
            'foto_perfil': reserva.usuario.foto_perfil.url if reserva.usuario.foto_perfil else None
        },
        'sessao': {
            'filme': reserva.sessao.filme.titulo,
            'sala': reserva.sessao.sala.nome,
            'cinema': reserva.sessao.sala.cinema.nome,
            'horario': reserva.sessao.horario.strftime('%d/%m/%Y %H:%M'),
            'tipo': reserva.sessao.get_tipo_display(),
            'idioma': reserva.sessao.get_idioma_display()
        },
        'data_hora_reserva': reserva.data_hora_reserva.strftime('%d/%m/%Y %H:%M'),
        'valor': str(reserva.valor),
        'status': reserva.get_status_display(),
        'status_class': 'success' if reserva.status == 'confirmada' else 'warning' if reserva.status == 'pendente' else 'danger',
        'ingressos': ingressos_data,
        'total_ingressos': len(ingressos_data)
    }
    
    return JsonResponse(data)