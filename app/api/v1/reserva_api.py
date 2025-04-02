from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import inject, Provide
from uuid import UUID

from app.core.di.container import Container
from app.core.commons.responses import RespostaDados, RespostaPaginada

from app.schema.reserva_schema import (
    ReservaFiltros,
    ReservaResponse,
    ReservaCreate,
    ReservaUpdate,
    ReservaRecorrenteFiltros,
    ReservaRecorrenteResponse,
    ReservaRecorrenteUpdate,
    ReservaRecorrenteRegularCreate,
    ReservaRecorrenteSemestreCreate,
)
from app.services.reserva_service import ReservaService
from app.services.reserva_recorrente_service import ReservaRecorrenteService
from app.core.security.auth_dependencies import AuthDependencies
from app.model.usuario_model import Usuario


router = APIRouter(
    prefix="/reserva",
    tags=["reserva"],
    dependencies=[Depends(AuthDependencies.get_current_user)],
)


# Reservas Recorrentes (mais específicas primeiro)
@router.get("/recorrente", response_model=RespostaPaginada[ReservaRecorrenteResponse])
@inject
def listar_reservas_recorrentes(
    filtros: ReservaRecorrenteFiltros = Depends(),
    usuario: Usuario = Depends(AuthDependencies.get_current_user),
    service: ReservaRecorrenteService = Depends(
        Provide[Container.reserva_recorrente_service]
    ),
):
    """
    Lista todas as reservas recorrentes com filtros e paginação.
    Cada reserva recorrente possui uma identificação única que indica:
    - Frequência (DIARIO/SEMANAL/MENSAL)
    - Sala
    - Horário
    - Dias da semana (quando aplicável)
    """
    # Validação direta de acesso
    if not usuario.super_user:
        if filtros.usuario_id and filtros.usuario_id != usuario.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para acessar reservas de outros usuários"
            )
        filtros.usuario_id = usuario.id
    
    resultado = service.get_by_query(filtros)
    return RespostaPaginada(
        dados=resultado.items,
        paginacao=resultado.paginacao,
        mensagem="Lista de reservas recorrentes recuperada com sucesso",
    )


@router.get(
    "/recorrente/{reserva_id}", response_model=RespostaDados[ReservaRecorrenteResponse]
)
@inject
def obter_reserva_recorrente(
    reserva_id: UUID,
    usuario: Usuario = Depends(AuthDependencies.get_current_user),
    service: ReservaRecorrenteService = Depends(
        Provide[Container.reserva_recorrente_service]
    ),
):
    """
    Obtém os detalhes de uma reserva recorrente específica.
    Inclui a identificação única da série de reservas.
    """
    # Validação direta de acesso
    if not usuario.super_user:
        reserva = service.get_by_id(reserva_id)
        if reserva.usuario_id != usuario.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para acessar esta reserva recorrente"
            )
    
    reserva = service.get_by_id(reserva_id)
    return RespostaDados(
        dados=reserva, mensagem=f"Reserva recorrente encontrada: {reserva.motivo}"
    )


@router.post("/recorrente/regular", response_model=RespostaDados[ReservaRecorrenteResponse])
@inject
async def criar_reserva_recorrente_regular(
    reserva: ReservaRecorrenteRegularCreate,
    usuario: Usuario = Depends(AuthDependencies.get_current_user),
    service: ReservaRecorrenteService = Depends(
        Provide[Container.reserva_recorrente_service]
    ),
):
    """
    Cria uma nova reserva recorrente regular.
    A identificação é gerada automaticamente seguindo o padrão:
    - DIARIA: "DIARIA-SALA101-14H"
    - SEMANAL: "SEG-SALA101-14H"
    - MENSAL: "1ºDIA-SALA101-14H"
    """
    reserva.usuario_id = usuario.id
    dados = service.create_regular(reserva, usuario.id, usuario.curso)
    return RespostaDados(
        dados=dados,
        mensagem=f"Reserva recorrente regular criada com identificação: {dados.identificacao}",
    )


@router.post("/recorrente/semestre", response_model=RespostaDados[ReservaRecorrenteResponse])
@inject
async def criar_reserva_recorrente_semestre(
    reserva: ReservaRecorrenteSemestreCreate,
    usuario: Usuario = Depends(AuthDependencies.get_current_user),
    service: ReservaRecorrenteService = Depends(
        Provide[Container.reserva_recorrente_service]
    ),
):
    """
    Cria uma nova reserva recorrente baseada em um semestre.
    As datas de início e fim são automaticamente definidas com base no semestre informado.
    """
    reserva.usuario_id = usuario.id
    dados = service.create_semestre(reserva, usuario.id, usuario.curso  )
    return RespostaDados(
        dados=dados,
        mensagem=f"Reserva recorrente do semestre criada com identificação: {dados.identificacao}",
    )


@router.patch(
    "/recorrente/{reserva_id}", response_model=RespostaDados[ReservaRecorrenteResponse]
)
@inject
def atualizar_reserva_recorrente(
    reserva_id: UUID,
    reserva: ReservaRecorrenteUpdate,
    usuario: Usuario = Depends(AuthDependencies.get_current_user),
    service: ReservaRecorrenteService = Depends(
        Provide[Container.reserva_recorrente_service]
    ),
):
    """
    Atualiza uma reserva recorrente existente.
    A identificação pode ser atualizada se houver mudanças na frequência ou horário.
    """
    # Validação direta de acesso
    if not usuario.super_user:
        reserva_existente = service.get_by_id(reserva_id)
        if reserva_existente.usuario_id != usuario.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para atualizar esta reserva recorrente"
            )
    
    dados = service.update(reserva_id, reserva)
    return RespostaDados(
        dados=dados, mensagem=f"Reserva recorrente atualizada: {dados.motivo}"
    )


@router.delete(
    "/recorrente/{reserva_id}", response_model=RespostaDados[ReservaRecorrenteResponse]
)
@inject
def remover_reserva_recorrente(
    reserva_id: UUID,
    usuario: Usuario = Depends(AuthDependencies.get_current_user),
    service: ReservaRecorrenteService = Depends(
        Provide[Container.reserva_recorrente_service]
    ),
):
    """
    Remove uma reserva recorrente e todas as suas ocorrências futuras.
    """
    # Validação direta de acesso
    if not usuario.super_user:
        reserva = service.get_by_id(reserva_id)
        if reserva.usuario_id != usuario.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para remover esta reserva recorrente"
            )
    
    dados = service.delete(reserva_id)
    return RespostaDados(
        dados=dados, mensagem=f"Reserva recorrente removida: {dados.motivo}"
    )


@router.post(
    "/recorrente/{reserva_id}/recriar",
    response_model=RespostaDados[ReservaRecorrenteResponse],
)
@inject
def recriar_reservas_recorrentes(
    reserva_id: UUID,
    usuario: Usuario = Depends(AuthDependencies.get_current_user),
    service: ReservaRecorrenteService = Depends(
        Provide[Container.reserva_recorrente_service]
    ),
):
    """
    Recria todas as reservas individuais de uma reserva recorrente.
    Útil para casos onde as reservas foram excluídas acidentalmente ou precisam ser recriadas.
    """
    # Validação direta de acesso
    if not usuario.super_user:
        reserva = service.get_by_id(reserva_id)
        if reserva.usuario_id != usuario.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para recriar esta reserva recorrente"
            )
    
    dados = service.recriar_reservas(reserva_id)
    return RespostaDados(
        dados=dados, mensagem=f"Reservas recriadas com sucesso para: {dados.motivo}"
    )


# Reservas Simples (mais gerais depois)
@router.get("", response_model=RespostaPaginada[ReservaResponse])
@inject
def listar_reservas(
    filtros: ReservaFiltros = Depends(),
    usuario: Usuario = Depends(AuthDependencies.get_current_user),
    service: ReservaService = Depends(Provide[Container.reserva_service]),
):
    """Lista todas as reservas simples com filtros e paginação."""
    # Validação direta de acesso
    if not usuario.super_user:
        if filtros.usuario_id and filtros.usuario_id != usuario.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para acessar reservas de outros usuários"
            )
        filtros.usuario_id = usuario.id
    
    resultado = service.get_by_query(filtros)
    return RespostaPaginada(dados=resultado.items, paginacao=resultado.paginacao)


@router.get("/{reserva_id}", response_model=RespostaDados[ReservaResponse])
@inject
def obter_reserva(
    reserva_id: UUID,
    usuario: Usuario = Depends(AuthDependencies.get_current_user),
    service: ReservaService = Depends(Provide[Container.reserva_service]),
):
    """Obtém os detalhes de uma reserva específica."""
    # Validação direta de acesso
    if not usuario.super_user:
        reserva = service.get_by_id(reserva_id)
        if reserva.usuario_id != usuario.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para acessar esta reserva"
            )
    
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
    dados = service.create(reserva, usuario.id, usuario.curso)
    return RespostaDados(dados=dados)


@router.patch("/{reserva_id}", response_model=RespostaDados[ReservaResponse])
@inject
def atualizar_reserva(
    reserva_id: UUID,
    reserva: ReservaUpdate,
    usuario: Usuario = Depends(AuthDependencies.get_current_user),
    service: ReservaService = Depends(Provide[Container.reserva_service]),
):
    # Validação direta de acesso
    if not usuario.super_user:
        reserva_existente = service.get_by_id(reserva_id)
        if reserva_existente.usuario_id != usuario.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para atualizar esta reserva"
            )
    
    return RespostaDados(dados=service.update(reserva_id, reserva, usuario.id))


@router.delete("/{reserva_id}", response_model=RespostaDados[ReservaResponse])
@inject
def remover_reserva(
    reserva_id: UUID,
    usuario: Usuario = Depends(AuthDependencies.get_current_user),
    service: ReservaService = Depends(Provide[Container.reserva_service]),
):
    # Validação direta de acesso
    if not usuario.super_user:
        reserva = service.get_by_id(reserva_id)
        if reserva.usuario_id != usuario.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para remover esta reserva"
            )
    
    return RespostaDados(dados=service.delete(reserva_id, usuario.id))
