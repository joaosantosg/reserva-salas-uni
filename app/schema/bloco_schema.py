from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from app.core.commons.responses import ParametrosPaginacao, InformacoesPaginacao


class BlocoBase(BaseModel):
    """Schema base para bloco"""

    nome: str
    identificacao: str

    class Config:
        from_attributes = True


class BlocoCreate(BlocoBase):
    """Schema para criação de bloco"""

    pass


class BlocoUpdate(BaseModel):
    """Schema para atualização de bloco"""

    nome: Optional[str] = None
    identificacao: Optional[str] = None


class BlocoResponse(BlocoBase):
    """Schema para resposta de bloco"""

    id: UUID
    criado_em: datetime
    atualizado_em: datetime


class BlocoFiltros(ParametrosPaginacao):
    """Schema para filtros de busca de blocos"""

    nome: Optional[str] = None
    identificacao: Optional[str] = None


class BlocosPaginados(BaseModel):
    """Schema para resposta paginada de blocos"""

    items: List[BlocoResponse]
    paginacao: InformacoesPaginacao

    class Config:
        from_attributes = True
