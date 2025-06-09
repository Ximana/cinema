# apps/sessoes/filters.py
import django_filters
from django.utils import timezone
from apps.sessoes.models import Sessao

class SessaoFilter(django_filters.FilterSet):
    """Filtros personalizados para sessões"""
    
    # Filtros por data
    data_inicio = django_filters.DateFilter(field_name='horario__date', lookup_expr='gte')
    data_fim = django_filters.DateFilter(field_name='horario__date', lookup_expr='lte')
    
    # Filtros por horário
    horario_inicio = django_filters.TimeFilter(field_name='horario__time', lookup_expr='gte')
    horario_fim = django_filters.TimeFilter(field_name='horario__time', lookup_expr='lte')
    
    # Filtros por preço
    preco_min = django_filters.NumberFilter(field_name='preco_base', lookup_expr='gte')
    preco_max = django_filters.NumberFilter(field_name='preco_base', lookup_expr='lte')
    
    # Filtros por filme
    filme_titulo = django_filters.CharFilter(field_name='filme__titulo', lookup_expr='icontains')
    filme_diretor = django_filters.CharFilter(field_name='filme__diretor', lookup_expr='icontains')
    filme_classificacao = django_filters.CharFilter(field_name='filme__classificacao', lookup_expr='exact')
    
    # Filtros por cinema/sala
    cinema_nome = django_filters.CharFilter(field_name='sala__cinema__nome', lookup_expr='icontains')
    cinema_localizacao = django_filters.CharFilter(field_name='sala__cinema__localizacao', lookup_expr='icontains')
    
    # Filtros especiais
    apenas_hoje = django_filters.BooleanFilter(method='filtrar_apenas_hoje')
    proximos_dias = django_filters.NumberFilter(method='filtrar_proximos_dias')
    
    class Meta:
        model = Sessao
        fields = {
            'filme__genero': ['exact', 'icontains'],
            'tipo': ['exact'],
            'idioma': ['exact'],
            'sala__cinema': ['exact'],
        }
    
    def filtrar_apenas_hoje(self, queryset, name, value):
        """Filtrar apenas sessões de hoje"""
        if value:
            hoje = timezone.now().date()
            return queryset.filter(horario__date=hoje)
        return queryset
    
    def filtrar_proximos_dias(self, queryset, name, value):
        """Filtrar sessões dos próximos N dias"""
        if value:
            data_limite = timezone.now() + timezone.timedelta(days=value)
            return queryset.filter(
                horario__gte=timezone.now(),
                horario__lte=data_limite
            )
        return queryset