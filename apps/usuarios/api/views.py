from rest_framework import viewsets, generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser


from apps.usuarios.serializers import (
    UsuarioSerializer, 
    UsuarioRegistroSerializer,
    UsuarioLoginSerializer,
    FotoPerfilSerializer
)

Usuario = get_user_model()

class UsuarioViewSet(viewsets.ModelViewSet):
    """ViewSet para operações CRUD de usuários"""
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_permissions(self):
        """Permissões personalizadas para diferentes ações"""
        if self.action == 'retrieve':
            # Um usuário pode ver seus próprios detalhes
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'upload_foto']:
            # Um usuário pode atualizar seus próprios dados
            return [permissions.IsAuthenticated()]
        elif self.action == 'destroy':
            # Apenas administradores podem excluir usuários
            return [permissions.IsAdminUser()]
        elif self.action == 'list':
            # Apenas administradores podem listar todos os usuários
            return [permissions.IsAdminUser()]
        return super().get_permissions()
    
    def get_queryset(self):
        """Filtra o queryset baseado no tipo de usuário"""
        if self.request.user.is_staff or self.request.user.is_admin():
            return Usuario.objects.all()
        return Usuario.objects.filter(id=self.request.user.id)
    
    @action(detail=True, methods=['post'])
    def upload_foto(self, request, pk=None):
        """Action personalizada para upload de foto de perfil"""
        usuario = self.get_object()
        
        # Verificar se o usuário pode editar este perfil
        if not (request.user == usuario or request.user.is_admin()):
            return Response(
                {'erro': 'Você não tem permissão para editar este perfil.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = FotoPerfilSerializer(usuario, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'mensagem': 'Foto de perfil atualizada com sucesso.',
                'foto_perfil': serializer.data.get('foto_perfil')
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegistroUsuarioView(generics.CreateAPIView):
    """API View para registro de novos usuários"""
    serializer_class = UsuarioRegistroSerializer
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser]

class LoginUsuarioView(ObtainAuthToken):
    """API View para login de usuários"""
    serializer_class = UsuarioLoginSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                          context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'username': user.username,
            'nome': user.get_nome_completo(),
            'tipo': user.tipo
        })

class LogoutUsuarioView(APIView):
    """API View para logout de usuários"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Deletar o token do usuário para fazer logout
        request.user.auth_token.delete()
        return Response(
            {'mensagem': 'Logout realizado com sucesso.'},
            status=status.HTTP_200_OK
        )

class MeuPerfilView(generics.RetrieveUpdateAPIView):
    """API View para visualizar e atualizar o próprio perfil"""
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_object(self):
        """Retornar o usuário autenticado"""
        return self.request.user


class UploadFotoPerfilView(APIView):
    """API View específica para upload de foto de perfil"""
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        """Upload de nova foto de perfil"""
        serializer = FotoPerfilSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'mensagem': 'Foto de perfil atualizada com sucesso.',
                'foto_perfil': request.build_absolute_uri(serializer.instance.foto_perfil.url) if serializer.instance.foto_perfil else None
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        """Remover foto de perfil"""
        user = request.user
        if user.foto_perfil:
            user.foto_perfil.delete()
            user.save()
            return Response({'mensagem': 'Foto de perfil removida com sucesso.'})
        return Response(
            {'erro': 'Nenhuma foto de perfil para remover.'},
            status=status.HTTP_400_BAD_REQUEST
        )