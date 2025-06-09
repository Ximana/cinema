# apps/reservas/api/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.db import transaction
import json

from .models import Reserva, Ingresso
from apps.sessoes.models import Sessao
from apps.filmes.models import Filme
from apps.cinemas.models import Cinema, Sala

Usuario = get_user_model()

class SessaoResumoSerializer(serializers.ModelSerializer):
    """Serializer resumido para exibir informações da sessão"""
    filme_titulo = serializers.CharField(source='filme.titulo', read_only=True)
    filme_poster = serializers.ImageField(source='filme.poster', read_only=True)
    sala_nome = serializers.CharField(source='sala.nome', read_only=True)
    cinema_nome = serializers.CharField(source='sala.cinema.nome', read_only=True)
    cinema_localizacao = serializers.CharField(source='sala.cinema.localizacao', read_only=True)
    
    class Meta:
        model = Sessao
        fields = ('id', 'horario', 'preco_base', 'tipo', 'idioma', 
                  'filme_titulo', 'filme_poster', 'sala_nome', 
                  'cinema_nome', 'cinema_localizacao')

class IngressoSerializer(serializers.ModelSerializer):
    """Serializer para ingressos"""
    assentos_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Ingresso
        fields = ('id', 'numero', 'preco', 'desconto', 'tipo_desconto', 
                  'assentos', 'assentos_list', 'status', 'data_emissao')
        read_only_fields = ('numero', 'data_emissao')
    
    def get_assentos_list(self, obj):
        """Converter assentos JSON para lista"""
        try:
            return json.loads(obj.assentos) if obj.assentos else []
        except (json.JSONDecodeError, TypeError):
            return []

class ReservaSerializer(serializers.ModelSerializer):
    """Serializer completo para reservas"""
    sessao = SessaoResumoSerializer(read_only=True)
    ingressos = IngressoSerializer(many=True, read_only=True)
    usuario_nome = serializers.CharField(source='usuario.get_full_name', read_only=True)
    total_ingressos = serializers.SerializerMethodField()
    
    class Meta:
        model = Reserva
        fields = ('id', 'data_hora_reserva', 'valor', 'status', 'sessao', 
                  'ingressos', 'usuario_nome', 'total_ingressos')
        read_only_fields = ('data_hora_reserva', 'usuario')
    
    def get_total_ingressos(self, obj):
        """Retornar total de ingressos da reserva"""
        return obj.ingressos.count()

class CriarReservaSerializer(serializers.Serializer):
    """Serializer para criar uma nova reserva"""
    sessao_id = serializers.IntegerField()
    ingressos = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
        max_length=10,  # Máximo 10 ingressos por reserva
        help_text="Lista de ingressos com assentos e tipos de desconto"
    )
    
    def validate_sessao_id(self, value):
        """Validar se a sessão existe e está disponível"""
        try:
            sessao = Sessao.objects.get(id=value)
            # Verificar se a sessão não passou
            from django.utils import timezone
            if sessao.horario < timezone.now():
                raise serializers.ValidationError(_('Esta sessão já passou.'))
            return value
        except Sessao.DoesNotExist:
            raise serializers.ValidationError(_('Sessão não encontrada.'))
    
    def validate_ingressos(self, value):
        """Validar estrutura dos ingressos"""
        for ingresso in value:
            if 'assentos' not in ingresso:
                raise serializers.ValidationError(_('Cada ingresso deve ter assentos especificados.'))
            if 'tipo_desconto' not in ingresso:
                ingresso['tipo_desconto'] = 'nenhum'
            
            # Validar tipo de desconto
            tipos_validos = [choice[0] for choice in Ingresso.TIPO_DESCONTO_CHOICES]
            if ingresso['tipo_desconto'] not in tipos_validos:
                raise serializers.ValidationError(
                    _('Tipo de desconto inválido: {}').format(ingresso['tipo_desconto'])
                )
        
        return value
    
    def validate(self, data):
        """Validações adicionais"""
        sessao = Sessao.objects.get(id=data['sessao_id'])
        
        # Verificar disponibilidade de assentos
        assentos_solicitados = []
        for ingresso in data['ingressos']:
            assentos_solicitados.extend(ingresso['assentos'])
        
        # Verificar se há assentos duplicados na própria solicitação
        if len(assentos_solicitados) != len(set(assentos_solicitados)):
            raise serializers.ValidationError(_('Assentos duplicados na reserva.'))
        
        # Verificar se os assentos já estão ocupados
        reservas_existentes = Reserva.objects.filter(
            sessao=sessao,
            status__in=['pendente', 'confirmada']
        )
        
        assentos_ocupados = []
        for reserva in reservas_existentes:
            for ingr in reserva.ingressos.all():
                try:
                    assentos_ocupados.extend(json.loads(ingr.assentos))
                except (json.JSONDecodeError, TypeError):
                    continue
        
        assentos_conflito = set(assentos_solicitados) & set(assentos_ocupados)
        if assentos_conflito:
            raise serializers.ValidationError(
                _('Os seguintes assentos já estão ocupados: {}').format(
                    ', '.join(assentos_conflito)
                )
            )
        
        # Verificar capacidade da sala
        if len(assentos_solicitados) > sessao.sala.capacidade:
            raise serializers.ValidationError(
                _('Número de assentos excede a capacidade da sala.')
            )
        
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        """Criar reserva e ingressos"""
        sessao = Sessao.objects.get(id=validated_data['sessao_id'])
        usuario = self.context['request'].user
        
        # Calcular valor total
        valor_total = 0
        for ingresso_data in validated_data['ingressos']:
            preco_base = sessao.preco_base
            
            # Aplicar desconto
            if ingresso_data['tipo_desconto'] != 'nenhum':
                if ingresso_data['tipo_desconto'] == 'estudante':
                    preco_base *= 0.5  # 50% desconto
                elif ingresso_data['tipo_desconto'] == 'idoso':
                    preco_base *= 0.6  # 40% desconto
                elif ingresso_data['tipo_desconto'] == 'promocional':
                    preco_base *= 0.7  # 30% desconto
            
            valor_total += preco_base * len(ingresso_data['assentos'])
        
        # Criar reserva
        reserva = Reserva.objects.create(
            usuario=usuario,
            sessao=sessao,
            valor=valor_total,
            status='pendente'
        )
        
        # Criar ingressos
        for ingresso_data in validated_data['ingressos']:
            for assento in ingresso_data['assentos']:
                preco_base = sessao.preco_base
                desconto = ingresso_data['tipo_desconto'] != 'nenhum'
                
                # Aplicar desconto
                if desconto:
                    if ingresso_data['tipo_desconto'] == 'estudante':
                        preco_base *= 0.5
                    elif ingresso_data['tipo_desconto'] == 'idoso':
                        preco_base *= 0.6
                    elif ingresso_data['tipo_desconto'] == 'promocional':
                        preco_base *= 0.7
                
                Ingresso.objects.create(
                    reserva=reserva,
                    preco=preco_base,
                    desconto=desconto,
                    tipo_desconto=ingresso_data['tipo_desconto'],
                    assentos=json.dumps([assento]),
                    status='emitido'
                )
        
        return reserva