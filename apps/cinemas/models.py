# apps/cinemas/models.py
from django.db import models
from django.urls import reverse

class Cinema(models.Model):
    nome = models.CharField('Nome', max_length=100)
    localizacao = models.CharField('Localização', max_length=100)
    telefone = models.CharField('Telefone', max_length=15)

    class Meta:
        db_table = 'cinemas'
        verbose_name = 'Cinema'
        verbose_name_plural = 'Cinemas'
        ordering = ['nome']
        
    def __str__(self):
        return self.nome
        
    def get_absolute_url(self):
        return reverse('cinemas:detalhes', kwargs={'pk': self.pk})

class Sala(models.Model):
    cinema = models.ForeignKey(
        Cinema,
        on_delete=models.CASCADE,
        related_name='salas',
        verbose_name='Cinema'
    )
    nome = models.CharField('Nome', max_length=50)
    capacidade = models.IntegerField('Capacidade')
    
    class Meta:
        db_table = 'salas'
        verbose_name = 'Sala'
        verbose_name_plural = 'Salas'
        ordering = ['cinema', 'nome']
        
    def __str__(self):
        return f"{self.nome} - {self.cinema.nome}"
        
    def get_absolute_url(self):
        return reverse('cinemas:sala_detalhes', kwargs={'pk': self.pk})