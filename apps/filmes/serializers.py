# apps/filmes/serializers.py
from rest_framework import serializers
from apps.filmes.models import Filme
from apps.sessoes.models import Sessao
from apps.sessoes.serializers import SessaoListSerializer
from django.utils import timezone


class FilmeListSerializer(serializers.ModelSerializer):
    """Serializer para listagem de filmes"""
    total_sessoes = serializers.SerializerMethodField()
    proxima_sessao = serializers.SerializerMethodField()
    
    class Meta:
        model = Filme
        fields = ('id', 'titulo', 'sinopse', 'duracao_minutos', 'diretor', 
                  'classificacao', 'data_lancamento', 'genero', 'poster',
                  'total_sessoes', 'proxima_sessao')
    
    def get_total_sessoes(self, obj):
        """Contar total de sessões disponíveis do filme"""
        return obj.sessoes.filter(horario__gte=timezone.now()).count()
    
    def get_proxima_sessao(self, obj):
        """Retornar informações da próxima sessão do filme"""
        cinema_id = self.context.get('cinema_id')
        
        queryset = obj.sessoes.filter(horario__gte=timezone.now())
        
        # Se foi especificado um cinema, filtrar por ele
        if cinema_id:
            queryset = queryset.filter(sala__cinema_id=cinema_id)
        
        proxima_sessao = queryset.order_by('horario').first()
        
        if proxima_sessao:
            return {
                'id': proxima_sessao.id,
                'horario': proxima_sessao.horario,
                'preco_base': proxima_sessao.preco_base,
                'cinema': proxima_sessao.sala.cinema.nome,
                'sala': proxima_sessao.sala.nome,
                'tipo': proxima_sessao.tipo,
                'idioma': proxima_sessao.idioma
            }
        return None


class FilmeDetailSerializer(serializers.ModelSerializer):
    """Serializer detalhado para filme"""
    total_sessoes = serializers.SerializerMethodField()
    
    class Meta:
        model = Filme
        fields = ('id', 'titulo', 'sinopse', 'duracao_minutos', 'diretor', 
                  'classificacao', 'site_oficial', 'trailer_oficial_url',
                  'data_lancamento', 'genero', 'poster', 'data_registo',
                  'data_atualizacao', 'total_sessoes')
    
    def get_total_sessoes(self, obj):
        """Contar total de sessões disponíveis do filme"""
        return obj.sessoes.filter(horario__gte=timezone.now()).count()


class FilmeComSessoesSerializer(serializers.ModelSerializer):
    """Serializer para filme com suas sessões disponíveis"""
    sessoes_disponiveis = serializers.SerializerMethodField()
    total_sessoes = serializers.SerializerMethodField()
    
    class Meta:
        model = Filme
        fields = ('id', 'titulo', 'sinopse', 'duracao_minutos', 'diretor', 
                  'classificacao', 'site_oficial', 'trailer_oficial_url',
                  'data_lancamento', 'genero', 'poster', 'total_sessoes',
                  'sessoes_disponiveis')
    
    def get_total_sessoes(self, obj):
        """Contar total de sessões disponíveis do filme"""
        return obj.sessoes.filter(horario__gte=timezone.now()).count()
    
    def get_sessoes_disponiveis(self, obj):
        """Retornar todas as sessões disponíveis do filme"""
        sessoes = obj.sessoes.filter(
            horario__gte=timezone.now()
        ).select_related(
            'sala', 'sala__cinema'
        ).order_by('horario')
        
        return SessaoListSerializer(sessoes, many=True).data


class FilmeCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para criar/atualizar filmes"""
    
    class Meta:
        model = Filme
        fields = ('titulo', 'sinopse', 'duracao_minutos', 'diretor', 
                  'classificacao', 'site_oficial', 'trailer_oficial_url',
                  'data_lancamento', 'genero', 'poster')
    
    def validate_titulo(self, value):
        """Validar título único"""
        if self.instance and self.instance.titulo == value:
            return value
        
        if Filme.objects.filter(titulo=value).exists():
            raise serializers.ValidationError(
                'Já existe um filme com este título.'
            )
        return value
    
    def validate_duracao_minutos(self, value):
        """Validar duração"""
        if value <= 0:
            raise serializers.ValidationError(
                'A duração deve ser maior que zero.'
            )
        return value
