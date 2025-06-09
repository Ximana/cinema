# apps/reservas/models.py
import uuid
from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator
from apps.usuarios.models import Usuario
from apps.sessoes.models import Sessao

class Reserva(models.Model):
    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
    )
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='reservas',
        verbose_name='Usuário'
    )
    sessao = models.ForeignKey(
        Sessao,
        on_delete=models.CASCADE,
        related_name='reservas',
        verbose_name='Sessão'
    )
    data_hora_reserva = models.DateTimeField('Data e Hora da Reserva', auto_now_add=True)
    valor = models.DecimalField(
        'Valor Total',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    status = models.CharField(
        'Status',
        max_length=50,
        choices=STATUS_CHOICES,
        default='pendente'
    )

    def pode_ser_cancelada(self):
        """Verificar se a reserva pode ser cancelada"""
        from django.utils import timezone
        from datetime import timedelta
    
        if self.status == 'cancelada':
            return False
        
        limite_cancelamento = self.sessao.horario - timedelta(hours=2)
        return timezone.now() <= limite_cancelamento

    def total_ingressos(self):
        """Retornar total de ingressos da reserva"""
        return self.ingressos.count()
    
    class Meta:
        db_table = 'reservas'
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-data_hora_reserva']
        
    def __str__(self):
        return f"Reserva {self.pk} - {self.usuario.get_nome_completo()} - {self.sessao}"
        
    def get_absolute_url(self):
        return reverse('administracao:reserva_detalhe', kwargs={'pk': self.pk})

def gerar_numero_ingresso():
    """Gera um número único para o ingresso."""
    return str(uuid.uuid4()).replace('-', '').upper()[:12]

class Ingresso(models.Model):
    TIPO_DESCONTO_CHOICES = (
        ('estudante', 'Estudante'),
        ('idoso', 'Idoso'),
        ('promocional', 'Promocional'),
        ('nenhum', 'Nenhum'),
    )
    
    STATUS_CHOICES = (
        ('emitido', 'Emitido'),
        ('utilizado', 'Utilizado'),
        ('cancelado', 'Cancelado'),
    )
    
    reserva = models.ForeignKey(
        Reserva,
        on_delete=models.CASCADE,
        related_name='ingressos',
        verbose_name='Reserva'
    )
    numero = models.CharField(
        'Número',
        max_length=12,
        unique=True,
        default=gerar_numero_ingresso
    )
    preco = models.DecimalField(
        'Preço',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    desconto = models.BooleanField('Desconto Aplicado', default=False)
    tipo_desconto = models.CharField(
        'Tipo de Desconto',
        max_length=20,
        choices=TIPO_DESCONTO_CHOICES,
        default='nenhum'
    )
    assentos = models.TextField(
        'Assentos',
        help_text='Assentos reservados (formato JSON)'
    )
    status = models.CharField(
        'Status',
        max_length=50,
        choices=STATUS_CHOICES,
        default='emitido'
    )
    data_emissao = models.DateTimeField('Data de Emissão', auto_now_add=True)
    
    class Meta:
        db_table = 'ingressos'
        verbose_name = 'Ingresso'
        verbose_name_plural = 'Ingressos'
        ordering = ['reserva', 'numero']
        
    def __str__(self):
        return f"Ingresso {self.numero} - {self.reserva.sessao.filme.titulo}"
        
    def get_absolute_url(self):
        return reverse('reservas:ingresso_detalhes', kwargs={'pk': self.pk})
    
    def save(self, *args, **kwargs):
        """Garantir que o número seja único ao salvar."""
        if not self.numero:
            while True:
                numero_temp = gerar_numero_ingresso()
                if not Ingresso.objects.filter(numero=numero_temp).exists():
                    self.numero = numero_temp
                    break
        super().save(*args, **kwargs)