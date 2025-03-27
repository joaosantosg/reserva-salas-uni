from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide
from uuid import UUID

from app.core.di.container import Container
from app.core.security.jwt import JWTManager
from app.core.commons.responses import RespostaDados, RespostaPaginada

from app.schema.reserva_schema import (
    ReservaFiltros,
    ReservaResponse,
    ReservaCreate,
    ReservaUpdate,
    ReservaRecorrenteFiltros,
    ReservaRecorrenteResponse,
    ReservaRecorrenteCreate,
    ReservaRecorrenteUpdate
)
from app.services.reserva_service import ReservaService
from app.services.reserva_recorrente_service import ReservaRecorrenteService
from app.core.security.auth_dependencies import AuthDependencies
from app.model.usuario_model import Usuario

router = APIRouter(
    prefix="/reserva",
    tags=["reserva"],
    # dependencies=[Depends(JWTManager.verify_token)]
)

# Endpoints para Reservas
@router.get("", response_model=RespostaPaginada[ReservaResponse])
@inject
def listar_reservas(
    filtros: ReservaFiltros = Depends(),
    service: ReservaService = Depends(Provide[Container.reserva_service]),
):
    resultado = service.get_by_query(filtros)
    return RespostaPaginada(
        dados=resultado.items,
        paginacao=resultado.paginacao
    )

@router.get("/{reserva_id}", response_model=RespostaDados[ReservaResponse])
@inject
def obter_reserva(
    reserva_id: UUID,
    service: ReservaService = Depends(Provide[Container.reserva_service]),
):
    reserva = service.get_by_id(reserva_id)
    return RespostaDados(dados=reserva)

@router.post("", response_model=RespostaDados[ReservaResponse])
@inject
async def criar_reserva(
    reserva: ReservaCreate,
    usuario: Usuario = Depends(AuthDependencies.get_current_user),
    service: ReservaService = Depends(Provide[Container.reserva_service]),
):
    reserva.usuario_id = usuario.id
    dados = service.create(reserva, usuario.id)
    return RespostaDados(dados=dados)

@router.patch("/{reserva_id}", response_model=RespostaDados[ReservaResponse])
@inject
def atualizar_reserva(
    reserva_id: UUID,
    reserva: ReservaUpdate,
    service: ReservaService = Depends(Provide[Container.reserva_service]),
):
    return RespostaDados(dados=service.update(reserva_id, reserva))

@router.delete("/{reserva_id}", response_model=RespostaDados[ReservaResponse])
@inject
def remover_reserva(
    reserva_id: UUID,
    service: ReservaService = Depends(Provide[Container.reserva_service]),
):
    return RespostaDados(dados=service.delete(reserva_id))

# Endpoints para Reservas Recorrentes
@router.get("/recorrente", response_model=RespostaPaginada[ReservaRecorrenteResponse])
@inject
def listar_reservas_recorrentes(
    filtros: ReservaRecorrenteFiltros = Depends(),
    service: ReservaRecorrenteService = Depends(Provide[Container.reserva_recorrente_service]),
):
    """
    Lista todas as reservas recorrentes com filtros e paginação.
    Cada reserva recorrente possui uma identificação única que indica:
    - Frequência (DIARIA/SEMANAL/MENSAL)
    - Sala
    - Horário
    - Dias da semana (quando aplicável)
    """
    resultado = service.get_by_query(filtros)
    return RespostaPaginada(
        dados=resultado.items,
        paginacao=resultado.paginacao,
        mensagem="Lista de reservas recorrentes recuperada com sucesso"
    )

@router.get("/recorrente/{reserva_id}", response_model=RespostaDados[ReservaRecorrenteResponse])
@inject
def obter_reserva_recorrente(
    reserva_id: UUID,
    service: ReservaRecorrenteService = Depends(Provide[Container.reserva_recorrente_service]),
):
    """
    Obtém os detalhes de uma reserva recorrente específica.
    Inclui a identificação única da série de reservas.
    """
    reserva = service.get_by_id(reserva_id)
    return RespostaDados(
        dados=reserva,
        mensagem=f"Reserva recorrente encontrada: {reserva.motivo}"
    )

@router.post("/recorrente", response_model=RespostaDados[ReservaRecorrenteResponse])
@inject
async def criar_reserva_recorrente(
    reserva: ReservaRecorrenteCreate,
    usuario: Usuario = Depends(AuthDependencies.get_current_user),
    service: ReservaRecorrenteService = Depends(Provide[Container.reserva_recorrente_service]),
):
    """
    Cria uma nova reserva recorrente.
    A identificação é gerada automaticamente seguindo o padrão:
    - DIARIA: "DIARIA-SALA101-14H"
    - SEMANAL: "SEG-SALA101-14H"
    - MENSAL: "1ºDIA-SALA101-14H"
    """
    reserva.usuario_id = usuario.id
    dados = service.create(reserva)
    return RespostaDados(
        dados=dados,
        mensagem=f"Reserva recorrente criada com identificação: {dados.motivo}"
    )

@router.patch("/recorrente/{reserva_id}", response_model=RespostaDados[ReservaRecorrenteResponse])
@inject
def atualizar_reserva_recorrente(
    reserva_id: UUID,
    reserva: ReservaRecorrenteUpdate,
    service: ReservaRecorrenteService = Depends(Provide[Container.reserva_recorrente_service]),
):
    """
    Atualiza uma reserva recorrente existente.
    A identificação pode ser atualizada se houver mudanças na frequência ou horário.
    """
    dados = service.update(reserva_id, reserva)
    return RespostaDados(
        dados=dados,
        mensagem=f"Reserva recorrente atualizada: {dados.motivo}"
    )

@router.delete("/recorrente/{reserva_id}", response_model=RespostaDados[ReservaRecorrenteResponse])
@inject
def remover_reserva_recorrente(
    reserva_id: UUID,
    service: ReservaRecorrenteService = Depends(Provide[Container.reserva_recorrente_service]),
):
    """
    Remove uma reserva recorrente e todas as suas ocorrências futuras.
    """
    dados = service.delete(reserva_id)
    return RespostaDados(
        dados=dados,
        mensagem=f"Reserva recorrente removida: {dados.motivo}"
    )

@router.post("/recorrente/{reserva_id}/recriar", response_model=RespostaDados[ReservaRecorrenteResponse])
@inject
def recriar_reservas_recorrentes(
    reserva_id: UUID,
    service: ReservaRecorrenteService = Depends(Provide[Container.reserva_recorrente_service]),
):
    """
    Recria todas as reservas individuais de uma reserva recorrente.
    Útil para casos onde as reservas foram excluídas acidentalmente ou precisam ser recriadas.
    """
    dados = service.recriar_reservas(reserva_id)
    return RespostaDados(
        dados=dados,
        mensagem=f"Reservas recriadas com sucesso para: {dados.motivo}"
    ) 