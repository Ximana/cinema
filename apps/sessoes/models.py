# apps/sessoes/models.py
from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator
from apps.cinemas.models import Sala
from apps.filmes.models import Filme

class Sessao(models.Model):
    TIPO_IDIOMA_CHOICES = (
        ('legendado', 'Legendado'),
        ('dublado', 'Dublado'),
    )
    TIPO_SESSAO_CHOICES = (
        ('2d', '2D'),
        ('3d', '3D'),
        ('imax', 'IMAX'),
    )
    
    sala = models.ForeignKey(
        Sala,
        on_delete=models.CASCADE,
        related_name='sessoes',
        verbose_name='Sala'
    )
    filme = models.ForeignKey(
        Filme,
        on_delete=models.CASCADE,
        related_name='sessoes',
        verbose_name='Filme'
    )
    horario = models.DateTimeField('Horário')
    preco_base = models.DecimalField(
        'Preço Base',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    tipo = models.CharField(
        'Tipo de Sessão',
        max_length=10,
        choices=TIPO_SESSAO_CHOICES,
        default='2d'
    )
    idioma = models.CharField(
        'Idioma da Sessão',
        max_length=10,
        choices=TIPO_IDIOMA_CHOICES,
        default='legendado'
    )
    
    class Meta:
        db_table = 'sessoes'
        verbose_name = 'Sessão'
        verbose_name_plural = 'Sessões'
        ordering = ['horario']
        
    def __str__(self):
        return f"{self.filme.titulo} - {self.sala.nome} - {self.horario.strftime('%d/%m/%Y %H:%M')}"
        
    def get_absolute_url(self):
        return reverse('sessoes:detalhes', kwargs={'pk': self.pk})
