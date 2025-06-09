# apps/usuarios/models.py
import uuid
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
"""
def usuario_foto_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4().hex}.{ext}'
    return os.path.join('usuarios/perfil', filename)
"""
def usuario_foto_path(instance, filename):
    """
    Função otimizada para Cloudinary
    """
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4().hex}.{ext}'
    # Use '/' ao invés de os.path.join para Cloudinary
    return f'usuarios/perfil/{filename}'

class Usuario(AbstractUser):
    TIPO_USUARIO_CHOICES = (
        ('regular', 'Regular'),
        ('admin', 'Administrador'),
    )
    
    # Campos adicionais de usuário
    numero_bi = models.CharField(
        'Número do BI',
        max_length=20,
        unique=True,
        null=True,
        blank=True
    )
    
    email = models.EmailField(
        'Email',
        max_length=100,
        unique=True
    )
    
    data_nascimento = models.DateField(
        'Data de Nascimento',
        null=True,
        blank=True
    )
    
    telefone = models.CharField(
        'Telefone',
        max_length=20,
        blank=True,
        null=True
    )
    
    tipo = models.CharField(
        'Tipo de Usuário',
        max_length=20,
        choices=TIPO_USUARIO_CHOICES,
        default='regular'
    )
    
    foto_perfil = models.ImageField(
        'Foto de Perfil',
        upload_to=usuario_foto_path,
        blank=True,
        null=True
    )
    
    data_registo = models.DateTimeField(
        'Data de Cadastro',
        auto_now_add=True
    )
    
    data_atualizacao = models.DateTimeField(
        'Data de Atualização',
        auto_now=True
    )
    
    def get_nome_completo(self):
        """Retorna o nome completo do usuário."""
        return self.get_full_name() or self.username
    
    def is_admin(self):
        """Verifica se o usuário é um administrador."""
        return self.tipo == 'admin'

    def tem_reservas_ativas(self):
        """Verificar se o usuário tem reservas ativas"""
        return self.reservas.filter(status__in=['pendente', 'confirmada']).exists()

    def total_reservas(self):
        """Retornar total de reservas do usuário"""
        return self.reservas.count()
    
    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['first_name', 'last_name']
        
    def __str__(self):
        return self.get_full_name() or self.username
        
    def get_absolute_url(self):
        return reverse('usuarios:detalhes', kwargs={'pk': self.pk})
