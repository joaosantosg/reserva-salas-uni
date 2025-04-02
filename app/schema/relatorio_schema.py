from datetime import date
from typing import List
from pydantic import BaseModel, Field
from app.schema.sala_schema import SalaResponse
from app.schema.usuario_schema import UsuarioResponse

class ReservasPorSalaResponse(BaseModel):
    """Schema para relatório de reservas por sala"""
    sala: SalaResponse
    quantidade: int = Field(..., description="Quantidade de reservas")
    periodo_inicio: date = Field(..., description="Data inicial do período")
    periodo_fim: date = Field(..., description="Data final do período")

class ReservasPorUsuarioResponse(BaseModel):
    """Schema para relatório de reservas por usuário"""
    usuario: UsuarioResponse
    quantidade: int = Field(..., description="Quantidade de reservas")
    periodo_inicio: date = Field(..., description="Data inicial do período")
    periodo_fim: date = Field(..., description="Data final do período")

class ReservasPorPeriodoResponse(BaseModel):
    """Schema para relatório de reservas por período"""
    data: date = Field(..., description="Data do período")
    quantidade: int = Field(..., description="Quantidade de reservas")
    sala_id: str = Field(..., description="ID da sala")

class OcupacaoPorSalaResponse(BaseModel):
    """Schema para relatório de ocupação por sala"""
    sala: SalaResponse
    taxa_ocupacao: float = Field(..., description="Taxa de ocupação em porcentagem")
    data: date = Field(..., description="Data da análise")
    total_horas: float = Field(..., description="Total de horas reservadas")
    total_horas_disponiveis: float = Field(..., description="Total de horas disponíveis")

class DashboardStatsResponse(BaseModel):
    """Schema para estatísticas gerais do dashboard"""
    total_reservas: int = Field(..., description="Total de reservas")
    total_salas: int = Field(..., description="Total de salas")
    total_usuarios: int = Field(..., description="Total de usuários")
    reservas_hoje: int = Field(..., description="Reservas para hoje")
    reservas_semana: int = Field(..., description="Reservas para esta semana")
    reservas_mes: int = Field(..., description="Reservas para este mês")
    salas_mais_ocupadas: List[ReservasPorSalaResponse] = Field(..., description="Top 5 salas mais ocupadas")
    usuarios_mais_ativos: List[ReservasPorUsuarioResponse] = Field(..., description="Top 5 usuários mais ativos") 