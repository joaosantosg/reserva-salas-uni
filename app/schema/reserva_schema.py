from datetime import datetime, date, time
from typing import List, Optional
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict, ValidationInfo

from app.core.commons.responses import ParametrosPaginacao, InformacoesPaginacao
from app.schema.sala_schema import SalaResponse
from app.schema.usuario_schema import UsuarioResponse


class FrequenciaRecorrencia(str, Enum):
    """Enum para frequência de recorrência"""

    DIARIO = "DIARIO"
    SEMANAL = "SEMANAL"
    MENSAL = "MENSAL"


class TipoReservaRecorrente(str, Enum):
    """Enum para tipo de reserva recorrente"""
    REGULAR = "REGULAR"
    SEMESTRE = "SEMESTRE"


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

    motivo: str = Field(..., description="Motivo da reserva recorrente")
    identificacao: Optional[str] = Field(None, description="Identificação da reserva recorrente, no formato 'DIARIO-SALA101-14H', caso não seja informado, será gerado automaticamente")
    sala_id: UUID = Field(..., description="ID da sala")
    usuario_id: Optional[UUID] = Field(None, description="ID do usuario responsavel pela reserva recorrente")
    frequencia: FrequenciaRecorrencia = Field(..., description="Frequência da reserva recorrente, DIARIO, SEMANAL ou MENSAL")
    dia_da_semana: Optional[List[int]] = Field(None, description="Dia da semana (0=segunda, 6=domingo), Apenas para frequência SEMANAL")
    dia_do_mes: Optional[int] = Field(None, description="Dia do mês (1-31), Apenas para frequência MENSAL")
    hora_inicio: time = Field(..., description="Hora de início da reserva recorrente")
    hora_fim: time = Field(..., description="Hora de fim da reserva recorrente")
    excecoes: List[date] = Field(default=[], description="Exceções da reserva recorrente")
    tipo: TipoReservaRecorrente = Field(..., description="Tipo de reserva recorrente: REGULAR ou SEMESTRE")

    @field_validator("dia_da_semana")
    @classmethod
    def validate_dia_da_semana(cls, v: Optional[List[int]], info: ValidationInfo) -> Optional[List[int]]:
        if info.data.get("frequencia") == FrequenciaRecorrencia.SEMANAL:
            if not v:
                raise ValueError("Dia da semana é obrigatório para frequência semanal")
            if not all(0 <= dia <= 6 for dia in v):
                raise ValueError(
                    "Dias da semana devem estar entre 0 (segunda) e 6 (domingo)"
                )
        return v

    @field_validator("dia_do_mes")
    @classmethod
    def validate_dia_do_mes(cls, v: Optional[int], info: ValidationInfo) -> Optional[int]:
        if info.data.get("frequencia") == FrequenciaRecorrencia.MENSAL:
            if not v:
                raise ValueError("Dia do mês é obrigatório para frequência mensal")
            if not 1 <= v <= 31:
                raise ValueError("Dia do mês deve estar entre 1 e 31")
        return v

    model_config = ConfigDict(from_attributes=True)


class ReservaRecorrenteRegularCreate(ReservaRecorrenteBase):
    """Schema para criação de reserva recorrente regular"""
    data_inicio: date = Field(..., description="Data de início da reserva recorrente")
    data_fim: date = Field(..., description="Data de fim da reserva recorrente")
    tipo: TipoReservaRecorrente = Field(TipoReservaRecorrente.REGULAR, description="Tipo de reserva recorrente: REGULAR")


class ReservaRecorrenteSemestreCreate(ReservaRecorrenteBase):
    """Schema para criação de reserva recorrente por semestre"""
    semestre: str = Field(..., description="Semestre da reserva recorrente, no formato '2025.1'")
    tipo: TipoReservaRecorrente = Field(TipoReservaRecorrente.SEMESTRE, description="Tipo de reserva recorrente: SEMESTRE")

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
    semestre: Optional[str] = None


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
