#/apps/administracao/views/usuarios_views.py
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView, View
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from .models import Usuario
from .forms import UsuarioRegistroForm
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q
from django.http import JsonResponse
import json

# Importe explícito do backend personalizado (opcional, mas pode ajudar na depuração)
from .authentication import EmailPhoneUsernameAuthenticationBackend

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # Pode ser nome de usuário, email ou telefone
        password = request.POST.get('password')
        
        # Autenticação utilizando nosso backend personalizado
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Login realizado com sucesso!')
            return redirect('core:home')
        else:
            messages.error(request, 'Credenciais inválidas')
    
    return render(request, 'usuarios/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Logout realizado com sucesso!')
    return redirect('usuarios:login')


class UsuarioListView(LoginRequiredMixin, ListView):
    model = Usuario
    template_name = 'usuarios/listarUsuarios.html'
    context_object_name = 'usuarios'
    paginate_by = 10
    
    # Função para pesquisa e filtro de usuários
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Search query filter
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(username__icontains=search_query)
            )
        
        # Tipo de usuário filter
        tipo_usuario = self.request.GET.get('tipo_usuario', '')
        if tipo_usuario:
            queryset = queryset.filter(tipo=tipo_usuario)
        
        # Status filter - ajustando para usar is_active ao invés de status
        status = self.request.GET.get('status', '')
        if status == 'ativo':
            queryset = queryset.filter(is_active=True)
        elif status == 'inativo':
            queryset = queryset.filter(is_active=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add context for filters
        context['form'] = UsuarioRegistroForm()
        
        # Preserve filter and search parameters
        context['search_query'] = self.request.GET.get('search', '')
        context['tipo_usuario_selecionado'] = self.request.GET.get('tipo_usuario', '')
        context['status_selecionado'] = self.request.GET.get('status', '')
        
        return context
    
    def post(self, request, *args, **kwargs):
        form = UsuarioRegistroForm(request.POST, request.FILES)
        if form.is_valid():
            usuario = form.save()
            
            # Adicionar mensagem de sucesso
            messages.success(request, f'Usuário {usuario.get_nome_completo()} cadastrado com sucesso!')
            
            return redirect(usuario.get_absolute_url())
        
        # If form is not valid, return to the list with errors
        self.object_list = self.get_queryset()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

class UsuarioDetailView(LoginRequiredMixin, DetailView):
    model = Usuario
    template_name = 'usuarios/detalhes.html'
    context_object_name = 'usuario'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Adiciona o formulário no contexto
        context['form'] = UsuarioRegistroForm(instance=self.object)
        
        return context

class UsuarioDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Usuario
    success_url = reverse_lazy('administracao:usuarios_lista')
    success_message = "Usuario removido com sucesso!"
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

class UsuarioUpdateView(LoginRequiredMixin, UpdateView):
    model = Usuario
    fields = ['first_name', 'last_name', 'email', 'telefone', 'numero_bi', 'data_nascimento']
    template_name = 'usuarios/detalhes.html'
    
    # funcao para retornar a pagina anterior
    def get_success_url(self):
        return reverse_lazy('usuarios:detalhes', kwargs={'pk': self.object.pk})
    
    def get_object(self, queryset=None):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Usuario atualizado com sucesso!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Erro ao atualizar usuario. Verifique os dados informados.')
        return redirect(reverse_lazy('usuarios:detalhes', kwargs={'pk': self.object.pk}))

class AtualizarFotoView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            foto = request.FILES.get('foto_perfil')
            if foto:
                # Se já existe uma foto, deletar a antiga
                if request.user.foto_perfil:
                    request.user.foto_perfil.delete()
                
                request.user.foto_perfil = foto
                request.user.save()
                messages.success(request, 'Foto de perfil atualizada com sucesso!')
            else:
                messages.error(request, 'Nenhuma foto foi selecionada.')
                
        except Exception as e:
            messages.error(request, 'Erro ao atualizar foto de perfil.')
        
        return redirect(reverse_lazy('usuarios:detalhes', kwargs={'pk': request.user.pk}))

class AlterarSenhaView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        senha_atual = request.POST.get('senha_atual')
        nova_senha = request.POST.get('nova_senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        
        if not request.user.check_password(senha_atual):
            messages.error(request, 'Senha atual incorreta.')
            return redirect(reverse_lazy('usuarios:detalhes', kwargs={'pk': request.user.pk}))
            
        if nova_senha != confirmar_senha:
            messages.error(request, 'As novas senhas não coincidem.')
            return redirect(reverse_lazy('usuarios:detalhes', kwargs={'pk': request.user.pk}))
            
        if len(nova_senha) < 8:
            messages.error(request, 'A nova senha deve ter pelo menos 8 caracteres.')
            return redirect(reverse_lazy('usuarios:detalhes', kwargs={'pk': request.user.pk}))
            
        # Verificar se a senha contém letras e números
        if not any(c.isalpha() for c in nova_senha) or not any(c.isdigit() for c in nova_senha):
            messages.error(request, 'A senha deve conter letras e números.')
            return redirect(reverse_lazy('usuarios:detalhes', kwargs={'pk': request.user.pk}))
        
        try:
            request.user.set_password(nova_senha)
            request.user.save()
            # Atualiza a sessão para manter o usuário logado
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Senha alterada com sucesso!')
        except Exception as e:
            messages.error(request, 'Erro ao alterar a senha. Tente novamente.')
            
        return redirect(reverse_lazy('usuarios:etalhes', kwargs={'pk': request.user.pk}))