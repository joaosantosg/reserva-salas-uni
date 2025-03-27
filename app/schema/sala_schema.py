from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from app.core.commons.responses import ParametrosPaginacao, InformacoesPaginacao
from app.schema.bloco_schema import BlocoResponse


class SalaBase(BaseModel):
    """Schema base para sala"""

    bloco_id: UUID
    identificacao_sala: str
    capacidade_maxima: int
    recursos: List[str] = []
    uso_restrito: bool = False
    curso_restrito: Optional[str] = None

    class Config:
        from_attributes = True


class SalaCreate(SalaBase):
    """Schema para criação de sala"""

    pass


class SalaUpdate(BaseModel):
    """Schema para atualização de sala"""

    identificacao_sala: Optional[str] = None
    capacidade_maxima: Optional[int] = None
    recursos: Optional[List[str]] = None
    uso_restrito: Optional[bool] = None
    curso_restrito: Optional[str] = None


class SalaResponse(SalaBase):
    """Schema para resposta de sala"""

    id: UUID
    criado_em: datetime
    atualizado_em: datetime


class SalaResponseDetalhada(SalaResponse):
    """Schema para resposta detalhada de sala, incluindo o bloco"""

    bloco: BlocoResponse


class SalaFiltros(ParametrosPaginacao):
    """Schema para filtros de busca de salas"""

    bloco_id: Optional[UUID] = None
    identificacao_sala: Optional[str] = None
    capacidade_minima: Optional[int] = None
    uso_restrito: Optional[bool] = None
    curso_restrito: Optional[str] = None


class SalasPaginadas(BaseModel):
    """Schema para resposta paginada de salas"""

    items: List[SalaResponse]
    paginacao: InformacoesPaginacao

    class Config:
        from_attributes = True
