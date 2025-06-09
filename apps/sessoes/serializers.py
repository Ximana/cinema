# apps/sessoes/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Sessao
from apps.cinemas.models import Cinema, Sala
from apps.filmes.models import Filme
#from apps.reservas.models import Reserva, Ingresso

Usuario = get_user_model()

class FilmeSerializer(serializers.ModelSerializer):
    """Serializer básico para filme"""
    class Meta:
        model = Filme
        fields = ('id', 'titulo', 'sinopse', 'duracao_minutos', 'diretor', 
                  'classificacao', 'site_oficial', 'trailer_oficial_url', 
                  'data_lancamento', 'genero', 'poster')

class CinemaSerializer(serializers.ModelSerializer):
    """Serializer básico para cinema"""
    class Meta:
        model = Cinema
        fields = ('id', 'nome', 'localizacao', 'telefone')

class SalaSerializer(serializers.ModelSerializer):
    """Serializer básico para sala"""
    cinema = CinemaSerializer(read_only=True)
    
    class Meta:
        model = Sala
        fields = ('id', 'nome', 'capacidade', 'cinema')

class SessaoListSerializer(serializers.ModelSerializer):
    """Serializer para listagem de sessões"""
    filme_titulo = serializers.CharField(source='filme.titulo', read_only=True)
    filme_genero = serializers.CharField(source='filme.genero', read_only=True)
    filme_classificacao = serializers.CharField(source='filme.classificacao', read_only=True)
    filme_duracao = serializers.IntegerField(source='filme.duracao_minutos', read_only=True)
    sala_nome = serializers.CharField(source='sala.nome', read_only=True)
    cinema_nome = serializers.CharField(source='sala.cinema.nome', read_only=True)
    cinema_localizacao = serializers.CharField(source='sala.cinema.localizacao', read_only=True)
    
    class Meta:
        model = Sessao
        fields = ('id', 'horario', 'preco_base', 'tipo', 'idioma', 
                  'filme_titulo', 'filme_genero', 'filme_classificacao', 
                  'filme_duracao', 'sala_nome', 'cinema_nome', 'cinema_localizacao')

class SessaoDetailSerializer(serializers.ModelSerializer):
    """Serializer detalhado para sessão"""
    filme = FilmeSerializer(read_only=True)
    sala = SalaSerializer(read_only=True)
    assentos_disponiveis = serializers.SerializerMethodField()
    
    class Meta:
        model = Sessao
        fields = ('id', 'horario', 'preco_base', 'tipo', 'idioma', 
                  'filme', 'sala', 'assentos_disponiveis')
    
    def get_assentos_disponiveis(self, obj):
        """Calcular assentos disponíveis (capacidade da sala - reservas confirmadas)"""
        from apps.reservas.models import Reserva, Ingresso
        
        # Contar ingressos emitidos para esta sessão
        ingressos_emitidos = Ingresso.objects.filter(
            reserva__sessao=obj,
            status__in=['emitido', 'utilizado']
        ).count()
        
        return obj.sala.capacidade - ingressos_emitidos

class SessaoCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para criar/atualizar sessões"""
    
    class Meta:
        model = Sessao
        fields = ('sala', 'filme', 'horario', 'preco_base', 'tipo', 'idioma')
    
    def validate(self, data):
        """Validações customizadas"""
        # Verificar se já existe uma sessão na mesma sala e horário
        sala = data.get('sala')
        horario = data.get('horario')
        
        if sala and horario:
            # Para updates, excluir a instância atual da verificação
            queryset = Sessao.objects.filter(sala=sala, horario=horario)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise serializers.ValidationError({
                    'horario': 'Já existe uma sessão agendada para esta sala neste horário.'
                })
        
        return data