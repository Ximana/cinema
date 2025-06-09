# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.db.models.functions import ExtractWeekDay
from datetime import date, datetime, timedelta
from .models import Filme
from apps.sessoes.models import Sessao
from apps.reservas.models import Reserva, Ingresso
from apps.cinemas.models import Cinema, Sala
from .forms import FilmeRegistroForm
from apps.sessoes.forms import SessaoForm

class FilmeListView(ListView):
    model = Filme
    template_name = 'filmes/listarFilmes.html'
    context_object_name = 'filmes'
    paginate_by = 10
    
    # Função para pesquisa de filmes
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(titulo__icontains=search_query) |
                Q(diretor__icontains=search_query) |
                Q(genero__icontains=search_query)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = FilmeRegistroForm()
        context['search_query'] = self.request.GET.get('search', '')
        return context
    
    def post(self, request, *args, **kwargs):
        form = FilmeRegistroForm(request.POST, request.FILES)
        if form.is_valid():
            filme = form.save()
            messages.success(request, 'Filme cadastrado com sucesso!')
            return redirect(filme.get_absolute_url())
        
        # Se o formulário não for válido, retorna à lista com os erros
        self.object_list = self.get_queryset()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)


class FilmeDetailView(LoginRequiredMixin, DetailView):
    model = Filme
    template_name = 'filmes/detalhes.html'
    context_object_name = 'filme'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoje = date.today()
        filme = self.object
        
        # Formulário para edição do filme
        context['form'] = FilmeRegistroForm(instance=filme)
        
        # Buscar todas as sessões do filme
        todas_sessoes = Sessao.objects.filter(filme=filme).order_by('horario')
        
        # Filtros para a lista de sessões
        data_filtro = self.request.GET.get('data')
        cinema_filtro = self.request.GET.get('cinema')
        tipo_filtro = self.request.GET.get('tipo')
        
        if data_filtro:
            data_filtro = datetime.strptime(data_filtro, '%Y-%m-%d').date()
            todas_sessoes = todas_sessoes.filter(horario__date=data_filtro)
        
        if cinema_filtro:
            todas_sessoes = todas_sessoes.filter(sala__cinema_id=cinema_filtro)
            
        if tipo_filtro:
            todas_sessoes = todas_sessoes.filter(tipo=tipo_filtro)
        
        # Paginação das sessões
        paginator = Paginator(todas_sessoes, 10)  # 10 sessões por página
        page_number = self.request.GET.get('page')
        sessoes_paginadas = paginator.get_page(page_number)
        context['sessoes'] = sessoes_paginadas
        
        # Próximas sessões (limitadas a 3 para o card lateral)
        proximas_sessoes = todas_sessoes.filter(
            horario__gte=datetime.now()
        ).order_by('horario')[:3]
        context['proximas_sessoes'] = proximas_sessoes
        
        # Lista de cinemas para filtro
        context['cinemas'] = Cinema.objects.all()
        
        # ESTATÍSTICAS
        
        # Buscar reservas confirmadas para este filme
        reservas_confirmadas = Reserva.objects.filter(
            sessao__filme=filme,
            status='confirmada'
        )
        
        # Total de ingressos vendidos
        total_ingressos = Ingresso.objects.filter(
            reserva__in=reservas_confirmadas,
            status='emitido'
        ).count()
        context['total_ingressos'] = total_ingressos
        
        # Receita total
        receita_total = reservas_confirmadas.aggregate(
            total=Sum('valor')
        )['total'] or 0
        context['receita_total'] = receita_total
        
        # Taxa de ocupação
        total_lugares = todas_sessoes.aggregate(
            total=Sum('sala__capacidade')
        )['total'] or 1  # Evitar divisão por zero
        
        taxa_ocupacao = (total_ingressos / total_lugares) * 100 if total_lugares > 0 else 0
        context['taxa_ocupacao'] = round(taxa_ocupacao, 1)
        
        # Ingressos por tipo de desconto
        ingressos_por_tipo = Ingresso.objects.filter(
            reserva__in=reservas_confirmadas
        ).values('tipo_desconto').annotate(
            count=Count('id')
        )
        
        # Inicialização dos contadores
        context['ingressos_inteira'] = 0
        context['ingressos_estudante'] = 0
        context['ingressos_idoso'] = 0
        context['ingressos_promocional'] = 0
        
        # Preenchimento dos contadores
        for tipo in ingressos_por_tipo:
            if tipo['tipo_desconto'] == 'nenhum':
                context['ingressos_inteira'] = tipo['count']
            elif tipo['tipo_desconto'] == 'estudante':
                context['ingressos_estudante'] = tipo['count']
            elif tipo['tipo_desconto'] == 'idoso':
                context['ingressos_idoso'] = tipo['count']
            elif tipo['tipo_desconto'] == 'promocional':
                context['ingressos_promocional'] = tipo['count']
        
        # Vendas por dia da semana
        # ExtractWeekDay retorna: 1 (domingo) a 7 (sábado)
        # Ajustamos para 0 (segunda) a 6 (domingo) para compatibilidade com JS
        vendas_dia_semana = Ingresso.objects.filter(
            reserva__in=reservas_confirmadas
        ).annotate(
            dia_semana=ExtractWeekDay('reserva__data_hora_reserva')
        ).values('dia_semana').annotate(
            count=Count('id')
        ).order_by('dia_semana')
        
        # Inicializa contadores para cada dia da semana
        dias_semana = {
            2: 'vendas_segunda',
            3: 'vendas_terca',
            4: 'vendas_quarta',
            5: 'vendas_quinta',
            6: 'vendas_sexta',
            7: 'vendas_sabado',
            1: 'vendas_domingo'
        }
        
        for dia in dias_semana.values():
            context[dia] = 0
            
        # Preenche os contadores com os valores reais
        for item in vendas_dia_semana:
            dia_key = dias_semana.get(item['dia_semana'])
            if dia_key:
                context[dia_key] = item['count']
        
        # Vendas por cinema
        vendas_por_cinema = Ingresso.objects.filter(
            reserva__in=reservas_confirmadas
        ).values(
            'reserva__sessao__sala__cinema__nome'
        ).annotate(
            total=Count('id')
        ).values('reserva__sessao__sala__cinema__nome', 'total')
        
        # Formatar os dados para o template
        context['vendas_por_cinema'] = [
            {'nome': item['reserva__sessao__sala__cinema__nome'], 'total': item['total']}
            for item in vendas_por_cinema
        ]
        
        # Evolução de vendas nos últimos 14 dias
        hoje = date.today()
        datas = []
        for i in range(14, -1, -1):
            data_atual = hoje - timedelta(days=i)
            datas.append(data_atual)
            
        evolucao_vendas = []
        for data in datas:
            ingressos_dia = Ingresso.objects.filter(
                reserva__in=reservas_confirmadas,
                reserva__data_hora_reserva__date=data
            ).count()
            
            evolucao_vendas.append({
                'data': data,
                'total': ingressos_dia
            })
            
        context['evolucao_vendas'] = evolucao_vendas
        context['form_sessao'] = SessaoForm()
        
        return context

    def post(self, request, *args, **kwargs):
        """Processar criação de nova sessão via modal"""
        self.object = self.get_object()
        
        if request.POST.get('action') == 'criar_sessao':
            form_sessao = SessaoForm(request.POST)
            if form_sessao.is_valid():
                sessao = form_sessao.save(commit=False)
                sessao.filme = self.object
                sessao.save()
                
                messages.success(
                    request, 
                    f'Sessão criada com sucesso para {sessao.horario.strftime("%d/%m/%Y às %H:%M")}!'
                )
                return redirect('filmes:detalhes', pk=self.object.pk)
            else:
                messages.error(request, 'Erro ao criar sessão. Verifique os dados informados.')
        
        # Se chegou aqui, houve erro - recarregar página com formulário
        context = self.get_context_data(**kwargs)
        context['form_sessao'] = form_sessao if 'form_sessao' in locals() else SessaoForm()
        return self.render_to_response(context)


class FilmeUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Filme
    form_class = FilmeRegistroForm
    template_name = 'filmes/detalhes.html'  # Apontamos para detalhe.html já que o modal está lá
    success_message = "Dados do filme %(titulo)s foram atualizados com sucesso!"
    
    def get_success_url(self):
        return reverse_lazy('filmes:detalhes', kwargs={'pk': self.object.pk})
    
    def form_invalid(self, form):
        # Em caso de erro, retorna para a página de detalhes com o formulário e erros
        return render(self.request, self.template_name, {
            'filme': self.get_object(),
            'form': form
        })


class FilmeDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Filme
    success_url = reverse_lazy('filmes:lista')
    success_message = "Filme removido com sucesso!"
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)