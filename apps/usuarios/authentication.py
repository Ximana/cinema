# usuarios/authentication.py
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.contrib.auth import get_user_model

class EmailPhoneUsernameAuthenticationBackend(ModelBackend):
    """
    Autenticador personalizado que permite login com email, nome de usuário ou telefone
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        
        try:
            # Procurar usuário pelo nome de usuário, email ou telefone
            user = UserModel.objects.get(
                Q(username=username) | 
                Q(email=username) | 
                Q(telefone=username)
            )
            
            # Verificar a senha
            if user.check_password(password):
                return user
                
        except UserModel.DoesNotExist:
            return None
            
        return None