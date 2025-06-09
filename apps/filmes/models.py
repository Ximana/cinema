# apps/filmes/models.py
import uuid
from django.db import models
from django.urls import reverse
"""
def filme_poster_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4().hex}.{ext}'
    return os.path.join('filmes/poster', filename)
"""

def filme_poster_path(instance, filename):
    """
    Função otimizada para Cloudinary
    """
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4().hex}.{ext}'
    # Use '/' ao invés de os.path.join para Cloudinary
    return f'filmes/poster/{filename}'

class Filme(models.Model):
    titulo = models.CharField('Título', max_length=100)
    sinopse = models.TextField('Sinopse')
    duracao_minutos = models.IntegerField('Duração (minutos)')
    diretor = models.CharField('Diretor', max_length=100)
    classificacao = models.CharField('Classificação', max_length=100)
    site_oficial = models.CharField('Site Oficial', max_length=200, blank=True, null=True)
    trailer_oficial_url = models.CharField('Trailer Oficial', max_length=200, blank=True, null=True)
    data_lancamento = models.DateField('Data de Lançamento')
    genero = models.CharField('Gênero', max_length=100)
    poster = models.ImageField(
        'Poster',
        upload_to=filme_poster_path,
        blank=True,
        null=True
    )
    data_registo = models.DateTimeField('Data de Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Data de Atualização', auto_now=True)
    
    class Meta:
        db_table = 'filmes'
        verbose_name = 'Filme'
        verbose_name_plural = 'Filmes'
        ordering = ['-data_lancamento', 'titulo']
        
    def __str__(self):
        return self.titulo
        
    def get_absolute_url(self):
        return reverse('filmes:detalhes', kwargs={'pk': self.pk})
