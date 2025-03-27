from typing import Optional
from fastapi import Depends, Request, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config.settings import settings
from app.core.security.jwt import JWTManager
from app.core.commons.exceptions import UnauthorizedException
from app.model.usuario_model import Usuario
from app.repository.usuario_repository import UsuarioRepository
from app.core.di.container import Container
from dependency_injector.wiring import inject, Provide
from uuid import UUID

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    scheme_name="JWT",
    description="JWT Authorization header using the Bearer scheme. Example: 'Bearer {token}'",
)

class AuthDependencies:
    """Dependências de autenticação para rotas FastAPI"""
    
    @staticmethod
    @inject
    async def get_current_user(
        request: Request,
        user_repository: UsuarioRepository = Depends(Provide[Container.usuario_repository])
    ) -> Usuario:
        """
        Obtém o usuário atual a partir do token JWT.
        Usar como dependência em rotas que requerem autenticação.
        
        Exemplo:
        @router.get("/me", response_model=UsuarioResponse)
        async def read_users_me(current_user: Usuario = Depends(AuthDependencies.get_current_user)):
            return current_user
        """
        try:
            payload = JWTManager.get_token_payload(request)
            # O payload já contém o UUID diretamente no 'sub'
            user_id = payload.get("sub")
            if not user_id:
                raise UnauthorizedException("Token inválido")
            
            # Convertendo a string do UUID para UUID
            user_id = UUID(user_id)
            
            user = user_repository.get_by_id(user_id)
            if not user:
                raise UnauthorizedException("Usuário não encontrado")
                
            if not user.ativo:
                raise UnauthorizedException("Usuário inativo")
            
            if user.bloqueado:
                raise UnauthorizedException("Usuário bloqueado")
                
            return user
            
        except Exception as e:
            raise UnauthorizedException(str(e))
    
    @staticmethod
    @inject
    async def get_current_active_superuser(
        current_user: Usuario = Depends(get_current_user)
    ) -> Usuario:
        """
        Obtém o usuário atual e verifica se é um super usuário.
        Usar como dependência em rotas que requerem privilégios de super usuário.
        
        Exemplo:
        @router.get("/admin", response_model=AdminResponse)
        async def read_admin(current_user: Usuario = Depends(AuthDependencies.get_current_active_superuser)):
            return current_user
        """
        user = await current_user
        if not user.super_user:
            raise UnauthorizedException(mensagem="Acesso negado: privilégios insuficientes")
        return user 