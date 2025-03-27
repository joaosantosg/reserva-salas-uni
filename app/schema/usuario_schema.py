from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.core.commons.responses import ParametrosPaginacao, InformacoesPaginacao


class UsuarioBase(BaseModel):
    """Schema base para usuário"""

    nome: str
    email: EmailStr
    matricula: str
    curso: str
    ativo: bool = True
    super_user: bool = False

    class Config:
        from_attributes = True


class UsuarioCreate(UsuarioBase):
    """Schema para criação de usuário"""

    senha: str


class UsuarioUpdate(BaseModel):
    """Schema para atualização de usuário"""

    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    matricula: Optional[str] = None
    curso: Optional[str] = None
    ativo: Optional[bool] = None
    senha: Optional[str] = None


class UsuarioResponse(UsuarioBase):
    """Schema para resposta de usuário"""

    id: UUID
    ultimo_login: Optional[datetime] = None
    criado_em: datetime
    atualizado_em: datetime


class UsuarioFiltros(ParametrosPaginacao):
    """Schema para filtros de busca de usuários"""

    nome: Optional[str] = None
    email: Optional[str] = None
    matricula: Optional[str] = None
    curso: Optional[str] = None
    ativo: Optional[bool] = None
    super_user: Optional[bool] = None


class UsuariosPaginados(BaseModel):
    """Schema para resposta paginada de usuários"""

    items: List[UsuarioResponse]
    paginacao: InformacoesPaginacao

    class Config:
        from_attributes = True
