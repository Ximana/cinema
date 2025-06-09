# serializers.py
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

Usuario = get_user_model()

class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer para o modelo de usuário"""
    class Meta:
        model = Usuario
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                  'numero_bi', 'data_nascimento', 'telefone', 'tipo', 
                  'foto_perfil', 'data_registo', 'data_atualizacao')
        read_only_fields = ('id', 'data_registo', 'data_atualizacao')
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 8}
        }
    
    def create(self, validated_data):
        """Criar um novo usuário com senha criptografada"""
        return Usuario.objects.create_user(**validated_data)
    
    def update(self, instance, validated_data):
        """Atualizar um usuário existente"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        
        if password:
            user.set_password(password)
            user.save()
            
        return user

class UsuarioRegistroSerializer(serializers.ModelSerializer):
    """Serializer para registro de usuários"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = Usuario
        fields = ('id', 'username', 'email', 'password', 'password_confirm', 'first_name', 
                  'last_name', 'numero_bi', 'data_nascimento', 'telefone', 'foto_perfil')
        
    def validate(self, data):
        """Validar se as senhas correspondem"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': _('As senhas não correspondem.')})
        return data
    
    def create(self, validated_data):
        """Criar um novo usuário com senha criptografada"""
        # Remover o campo password_confirm
        validated_data.pop('password_confirm')
        
        # Definir tipo padrão como 'regular' se não especificado
        if 'tipo' not in validated_data:
            validated_data['tipo'] = 'regular'
        
        # Criar o usuário
        return Usuario.objects.create_user(**validated_data)

class UsuarioLoginSerializer(serializers.Serializer):
    """Serializer para autenticação de usuários"""
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )
    
    def validate(self, data):
        """Validar e autenticar o usuário"""
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            # Aqui usamos o authenticate que usará nosso backend personalizado
            user = authenticate(
                request=self.context.get('request'),
                username=username,
                password=password
            )
            
            if not user:
                msg = _('Não foi possível autenticar com as credenciais fornecidas')
                raise serializers.ValidationError(msg, code='authentication')
        else:
            msg = _('Deve incluir "username" e "password"')
            raise serializers.ValidationError(msg, code='authentication')
            
        data['user'] = user
        return data

class FotoPerfilSerializer(serializers.ModelSerializer):
    """Serializer específico para upload de foto de perfil"""
    foto_perfil = serializers.ImageField(required=True)
    
    class Meta:
        model = Usuario
        fields = ('foto_perfil',)
    
    def validate_foto_perfil(self, value):
        """Validar arquivo de imagem"""
        # Validar tamanho do arquivo (máximo 5MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError(_('O arquivo não pode ser maior que 5MB.'))
        
        # Validar tipo de arquivo
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError(_('Apenas arquivos JPEG, PNG e GIF são permitidos.'))
        
        return value