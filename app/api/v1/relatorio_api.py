from datetime import datetime, date
from typing import List
from fastapi import APIRouter, Depends, Query
from app.services.relatorio_service import RelatorioService
from app.schema.relatorio_schema import (
    ReservasPorSalaResponse,
    ReservasPorUsuarioResponse,
    ReservasPorPeriodoResponse,
    OcupacaoPorSalaResponse,
    DashboardStatsResponse,
)
from app.core.security.auth_dependencies import AuthDependencies
from app.model.usuario_model import Usuario
from app.core.di.container import Container
from dependency_injector.wiring import inject, Provide

router = APIRouter(
    prefix="/relatorio",
    tags=["Relatórios"],
)

@router.get("/dashboard/stats", response_model=DashboardStatsResponse)
@inject
async def get_dashboard_stats(
    current_user: Usuario = Depends(AuthDependencies.get_current_user),
    relatorio_service: RelatorioService = Depends(Provide[Container.relatorio_service]),
):
    """Retorna estatísticas gerais para o dashboard"""
    return relatorio_service.get_dashboard_stats()

@router.get("/reservas/por-sala", response_model=List[ReservasPorSalaResponse])
@inject
async def get_reservas_por_sala(
    data_inicio: date = Query(..., description="Data inicial do período"),
    data_fim: date = Query(..., description="Data final do período"),
    current_user: Usuario = Depends(AuthDependencies.get_current_user),
    relatorio_service: RelatorioService = Depends(Provide[Container.relatorio_service]),
):
    """Retorna quantidade de reservas por sala em um período"""
    return relatorio_service.get_reservas_por_sala(data_inicio, data_fim)

@router.get("/reservas/por-usuario", response_model=List[ReservasPorUsuarioResponse])
@inject
async def get_reservas_por_usuario(
    data_inicio: date = Query(..., description="Data inicial do período"),
    data_fim: date = Query(..., description="Data final do período"),
    current_user: Usuario = Depends(AuthDependencies.get_current_user),
    relatorio_service: RelatorioService = Depends(Provide[Container.relatorio_service]),
):
    """Retorna quantidade de reservas por usuário em um período"""
    return relatorio_service.get_reservas_por_usuario(data_inicio, data_fim)

@router.get("/reservas/por-periodo", response_model=List[ReservasPorPeriodoResponse])
@inject
async def get_reservas_por_periodo(
    sala_id: str = Query(..., description="ID da sala"),
    data_inicio: date = Query(..., description="Data inicial do período"),
    data_fim: date = Query(..., description="Data final do período"),
    current_user: Usuario = Depends(AuthDependencies.get_current_user),
    relatorio_service: RelatorioService = Depends(Provide[Container.relatorio_service]),
):
    """Retorna quantidade de reservas por período para uma sala específica"""
    return relatorio_service.get_reservas_por_periodo(sala_id, data_inicio, data_fim)

@router.get("/ocupacao/por-sala", response_model=List[OcupacaoPorSalaResponse])
@inject
async def get_ocupacao_por_sala(
    data: date = Query(..., description="Data para análise de ocupação"),
    current_user: Usuario = Depends(AuthDependencies.get_current_user),
    relatorio_service: RelatorioService = Depends(Provide[Container.relatorio_service]),
):
    """Retorna taxa de ocupação por sala em uma data específica"""
    return relatorio_service.get_ocupacao_por_sala(data)

@router.get("/uso-salas")
@inject
async def gerar_relatorio_uso_salas(
    data_inicio: datetime = Query(..., description="Data inicial do relatório"),
    data_fim: datetime = Query(..., description="Data final do relatório"),
    current_user: Usuario = Depends(AuthDependencies.get_current_active_superuser),
    relatorio_service: RelatorioService = Depends(Provide[Container.relatorio_service]),
):
    """
    Gera relatório com estatísticas de uso das salas.
    Inclui:
    - Total de reservas por sala
    - Horários de pico
    - Taxa de ocupação
    Requer privilégios de superusuário.
    """
    return relatorio_service.gerar_relatorio_uso_salas(data_inicio, data_fim)
