# views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Cinema, Sala
from apps.sessoes.models import Sessao
from .forms import CinemaRegistroForm, SalaRegistroForm
from django.apps import apps
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required
import logging

class CinemaListView(ListView):
    model = Cinema
    template_name = 'cinemas/listarCinemas.html'
    context_object_name = 'cinemas'
    paginate_by = 10
    
    # Função para pesquisa de cinemas
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(nome__icontains=search_query) |
                Q(localizacao__icontains=search_query)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Verificar se já existe um formulário com erros no contexto
        if 'form' not in context:
            context['form'] = CinemaRegistroForm()
        context['search_query'] = self.request.GET.get('search', '')
        return context
    
    def post(self, request, *args, **kwargs):
        form = CinemaRegistroForm(request.POST, request.FILES)
        if form.is_valid():
            cinema = form.save()
            messages.success(request, 'Cinema cadastrado com sucesso!')
            return redirect(cinema.get_absolute_url())
        
        # Se o formulário não for válido, retorna à lista com os erros
        self.object_list = self.get_queryset()
        context = self.get_context_data(form=form)
        # Adicione uma mensagem de erro ao contexto
        messages.error(request, 'Ocorreram erros ao cadastrar o cinema. Por favor, verifique os campos.')
        return self.render_to_response(context)

class CinemaDetailView(LoginRequiredMixin, DetailView):
    model = Cinema
    template_name = 'cinemas/detalhes.html'
    context_object_name = 'cinema'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Adicionar o formulário de edição no contexto 
        context['form'] = CinemaRegistroForm(instance=self.object)
        
        # Obter todas as salas do cinema
        context['salas'] = Sala.objects.filter(cinema=self.object)
        
        # Obter todas as sessões associadas às salas do cinema
        context['sessoes'] = Sessao.objects.filter(
            sala__cinema=self.object
        ).select_related('filme', 'sala').order_by('horario')
        
        # Para formulário de adição de sala
        context['sala_form'] = SalaRegistroForm(initial={'cinema': self.object})
        
        return context
    
    # Melhorar o método post para lidar com diferentes tipos de submissões
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Verificar se é uma submissão para adicionar sala
        if 'adicionar_sala' in request.POST:
            form = SalaRegistroForm(request.POST)
            if form.is_valid():
                sala = form.save()
                messages.success(request, f'Sala "{sala.nome}" adicionada com sucesso!')
                return redirect(self.object.get_absolute_url())
            else:
                messages.error(request, 'Erro ao adicionar sala. Verifique os dados informados.')
                return self.render_to_response(self.get_context_data(sala_form=form))
        
        # Caso seja para editar o cinema (comportamento atual)
        else:
            form = CinemaRegistroForm(request.POST, request.FILES, instance=self.object)
            if form.is_valid():
                cinema = form.save()
                messages.success(request, 'Cinema atualizado com sucesso!')
                return redirect(cinema.get_absolute_url())
            else:
                messages.error(request, 'Erro ao atualizar cinema. Verifique os dados informados.')
                return self.render_to_response(self.get_context_data(form=form))

class CinemaUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Cinema
    form_class = CinemaRegistroForm
    template_name = 'cinemas/editarCinema.html'
    success_message = "Cinema atualizado com sucesso!"

class CinemaDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Cinema
    success_url = reverse_lazy('cinemas:lista')
    success_message = "Cinema removido com sucesso!"
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)