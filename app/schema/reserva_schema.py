from datetime import datetime, date, time
from typing import List, Optional, Dict, Any
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, validator

from app.core.commons.responses import ParametrosPaginacao, InformacoesPaginacao
from app.schema.sala_schema import SalaResponse
from app.schema.usuario_schema import UsuarioResponse

class FrequenciaRecorrencia(str, Enum):
    """Enum para frequência de recorrência"""
    DIARIA = "DIARIA"
    SEMANAL = "SEMANAL"
    MENSAL = "MENSAL"


class ReservaBase(BaseModel):
    """Schema base para reserva"""
    sala_id: UUID
    
    inicio: datetime
    fim: datetime
    usuario_id: Optional[UUID] = None
    motivo: str

    class Config:
        from_attributes = True


class ReservaCreate(ReservaBase):
    """Schema para criação de reserva"""
    pass


class ReservaUpdate(BaseModel):
    """Schema para atualização de reserva"""
    inicio: Optional[datetime] = None
    fim: Optional[datetime] = None
    motivo: Optional[str] = None


class ReservaResponse(ReservaBase):
    """Schema para resposta de reserva"""
    id: UUID
    criado_em: datetime
    atualizado_em: datetime
    sala: SalaResponse
    usuario: UsuarioResponse


class ReservaFiltros(ParametrosPaginacao):
    """Schema para filtros de busca de reservas"""
    sala_id: Optional[UUID] = None
    usuario_id: Optional[UUID] = None
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None


class ReservasPaginadas(BaseModel):
    """Schema para resposta paginada de reservas"""
    items: List[ReservaResponse]
    paginacao: InformacoesPaginacao

    class Config:
        from_attributes = True


class ReservaRecorrenteBase(BaseModel):
    """Schema base para reserva recorrente"""
    sala_id: UUID
    usuario_id: Optional[UUID] = None
    motivo: str
    frequencia: FrequenciaRecorrencia
    dia_da_semana: Optional[List[int]] = None  # Apenas para frequência semanal
    dia_do_mes: Optional[int] = None  # Apenas para frequência mensal
    hora_inicio: time
    hora_fim: time
    data_inicio: date
    data_fim: date
    excecoes: List[date] = []

    class Config:
        from_attributes = True

    @validator('dia_da_semana')
    def validate_dia_da_semana(cls, v, values):
        if 'frequencia' in values and values['frequencia'] == FrequenciaRecorrencia.SEMANAL:
            if not v:
                raise ValueError("Dia da semana é obrigatório para frequência semanal")
            if not all(0 <= dia <= 6 for dia in v):
                raise ValueError("Dias da semana devem estar entre 0 (segunda) e 6 (domingo)")
        return v

    @validator('dia_do_mes')
    def validate_dia_do_mes(cls, v, values):
        if 'frequencia' in values and values['frequencia'] == FrequenciaRecorrencia.MENSAL:
            if not v:
                raise ValueError("Dia do mês é obrigatório para frequência mensal")
            if not 1 <= v <= 31:
                raise ValueError("Dia do mês deve estar entre 1 e 31")
        return v


class ReservaRecorrenteCreate(ReservaRecorrenteBase):
    """Schema para criação de reserva recorrente"""
    pass


class ReservaRecorrenteUpdate(BaseModel):
    """Schema para atualização de reserva recorrente"""
    motivo: Optional[str] = None
    frequencia: Optional[FrequenciaRecorrencia] = None
    dia_da_semana: Optional[List[int]] = None
    data_inicio: Optional[date] = None
    hora_inicio: Optional[time] = None
    hora_fim: Optional[time] = None
    data_fim: Optional[date] = None
    excecoes: Optional[List[date]] = None


class ReservaRecorrenteResponse(ReservaRecorrenteBase):
    """Schema para resposta de reserva recorrente"""
    id: UUID
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True


class ReservaRecorrenteFiltros(ParametrosPaginacao):
    """Schema para filtros de busca de reservas recorrentes"""
    sala_id: Optional[UUID] = None
    usuario_id: Optional[UUID] = None
    frequencia: Optional[FrequenciaRecorrencia] = None
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None


class ReservasRecorrentesPaginadas(BaseModel):
    """Schema para resposta paginada de reservas recorrentes"""
    items: List[ReservaRecorrenteResponse]
    paginacao: InformacoesPaginacao

    class Config:
        from_attributes = True


class EstatisticaSala(BaseModel):
    """Estatísticas de uso de uma sala"""
    total_reservas: int
    horas_reservadas: float
    horarios_pico: dict
    taxa_ocupacao: float
    sala: SalaResponse


class RelatorioUsoSalas(BaseModel):
    """Relatório de uso das salas"""
    periodo: dict
    total_salas: int
    salas: List[EstatisticaSala]
    resumo: dict