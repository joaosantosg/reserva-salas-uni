from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
import re

from app.schema.usuario_schema import UsuarioResponse


# ------------------------
# Mixins de validação
# ------------------------


class SenhaValidacaoMixin(BaseModel):
    """Validação para senha segura"""

    @field_validator("senha", mode="before", check_fields=False)
    @classmethod
    def validar_senha(cls, v):
        if not re.match(
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", v
        ):
            # raise ValueError(
            #     'A senha deve conter pelo menos 8 caracteres, '
            #     'incluindo maiúsculas, minúsculas, números e caracteres especiais.'
            # )
            return v
        return v


class ConfirmacaoSenhaMixin(BaseModel):
    """Validação de confirmação de senha"""

    @field_validator("confirmar_senha", mode="before", check_fields=False)
    @classmethod
    def validar_confirmacao(cls, v, info):
        data = info.data
        if "senha" in data and v != data["senha"]:
            raise ValueError("As senhas não conferem.")
        if "nova_senha" in data and v != data["nova_senha"]:
            raise ValueError("As senhas não conferem.")
        return v


# ------------------------
# Requisições e Respostas
# ------------------------


class LoginRequisicao(SenhaValidacaoMixin):
    """Dados necessários para login"""

    matricula: str = Field(..., description="Matrícula do usuário")
    senha: str = Field(..., description="Senha do usuário")


class LoginResposta(BaseModel):
    """Resposta do login com tokens"""

    access_token: str
    refresh_token: str
    expires_in: datetime
    usuario: UsuarioResponse

    class Config:
        from_attributes = True


class AtualizarTokenRequisicao(BaseModel):
    """Dados necessários para atualizar token"""

    refresh_token: str = Field(..., description="Token de atualização")


class AtualizarTokenResposta(BaseModel):
    """Resposta da atualização do token"""

    access_token: str
    refresh_token: str
    expires_in: datetime
    usuario: UsuarioResponse

    class Config:
        from_attributes = True


class TokenPayload(BaseModel):
    """Payload do token JWT"""

    id: UUID
    matricula: str
    nome: str
    curso: str
    ativo: bool
    super_user: bool
    exp: datetime


# ------------------------
# Senhas
# ------------------------


class SenhaBase(SenhaValidacaoMixin, ConfirmacaoSenhaMixin):
    """Base para redefinição ou alteração de senha"""

    nova_senha: str = Field(..., description="Nova senha")
    confirmar_senha: str = Field(..., description="Confirmação da nova senha")

    @field_validator("nova_senha", mode="before")
    @classmethod
    def validar_nova_senha(cls, v):
        if not re.match(
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", v
        ):
            raise ValueError(
                "A nova senha deve conter pelo menos 8 caracteres, "
                "incluindo maiúsculas, minúsculas, números e caracteres especiais."
            )
        return v


class RecuperarSenhaRequisicao(BaseModel):
    """Requisição para recuperar senha"""

    matricula: str = Field(..., description="Matrícula do usuário")


class RedefinirSenhaRequisicao(SenhaBase):
    """Requisição para redefinição de senha"""

    token: str = Field(..., description="Token de redefinição de senha")


class AlterarSenhaRequisicao(SenhaBase):
    """Requisição para alteração de senha"""

    senha_atual: str = Field(..., description="Senha atual")
