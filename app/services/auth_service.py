from typing import List
from app.core.config.settings import settings
from app.core.security.jwt import JWTManager
from app.core.commons.exceptions import UnauthorizedException, NotFoundException
from app.model.usuario_model import Usuario
from app.repository.usuario_repository import UsuarioRepository
from app.schema.auth_schema import (
    LoginRequisicao,
    LoginResposta,
    AtualizarTokenRequisicao,
    AtualizarTokenResposta,
    RecuperarSenhaRequisicao,
    RedefinirSenhaRequisicao,
)
from app.schema.usuario_schema import UsuarioFiltros
from app.services.base_service import BaseService


class AuthService(BaseService):
    def __init__(self, user_repository: UsuarioRepository):
        self.user_repository = user_repository
        super().__init__(user_repository)

    def login(self, credentials: LoginRequisicao) -> LoginResposta:
        """
        Autentica o usuário e retorna tokens de acesso
        """
        user = self.user_repository.get_by_matricula(credentials.matricula)

        if not user:
            raise UnauthorizedException(mensagem="Matrícula ou senha incorretos")

        if not user.ativo:
            raise UnauthorizedException(mensagem="Conta não está ativa")

        if not user.verificar_senha(credentials.senha):
            raise UnauthorizedException(mensagem="Matrícula ou senha incorretos")

        # Gerar tokens com o ID do usuário como subject
        access_token = JWTManager.create_access_token(user)
        refresh_token = JWTManager.create_refresh_token(user)

        return LoginResposta(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            usuario=user,
        )

    def refresh_token(
        self, refresh_token: AtualizarTokenRequisicao
    ) -> AtualizarTokenResposta:
        """
        Renova o token de acesso usando re  fresh token
        """
        try:
            user_id = JWTManager.verify_refresh_token(refresh_token.refresh_token)
            user = self.user_repository.get_by_id(user_id)
            new_access_token = JWTManager.create_access_token(user)

            return AtualizarTokenResposta(
                access_token=new_access_token,
                refresh_token=refresh_token,
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            )
        except Exception:
            raise UnauthorizedException(mensagem="Refresh token inválido ou expirado")

    ## TODO: Implementar a recuperação de senha
    def forgot_password(self, request: RecuperarSenhaRequisicao) -> dict:
        """
        Inicia o processo de recuperação de senha
        """
        find_user = UsuarioFiltros()
        find_user.email = request.email
        user: List[Usuario] = self.user_repository.read_by_options(find_user)["founds"]

        if not user:
            raise NotFoundException(mensagem="Usuário não encontrado")

        # Enviar email
        # send_password_reset_email(user[0].email, reset_token)

        return {"message": "Função não implementada"}

    def reset_password(self, request: RedefinirSenhaRequisicao) -> dict:
        """
        Redefine a senha usando token de recuperação
        """
        if request.nova_senha != request.confirmar_senha:
            raise ValueError("Senhas não conferem")

        try:
            user_id = JWTManager.verify_password_reset_token(request.token)

            # Atualizar senha
            user = self.user_repository.get_by_id(user_id)
            if not user:
                raise NotFoundException(mensagem="Usuário não encontrado")

            user.set_senha(request.nova_senha)
            self.user_repository.update(user)

            return {"message": "Senha alterada com sucesso"}
        except Exception:
            raise UnauthorizedException(
                mensagem="Token de recuperação inválido ou expirado"
            )
