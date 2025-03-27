from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide
from uuid import UUID

from app.core.di.container import Container
from app.core.commons.responses import RespostaDados, RespostaPaginada, RespostaLista

from app.schema.sala_schema import (
    SalaFiltros,
    SalaResponse,
    SalaCreate,
    SalaUpdate,
    SalaResponseDetalhada,
)
from app.services.sala_service import SalaService
from app.core.security.auth_dependencies import AuthDependencies

router = APIRouter(
    prefix="/sala",
    tags=["Salas"],
    dependencies=[Depends(AuthDependencies.get_current_user)],
)


@router.get("", response_model=RespostaPaginada[SalaResponse])
@inject
def listar_salas(
    filtros: SalaFiltros = Depends(),
    service: SalaService = Depends(Provide[Container.sala_service]),
):
    """Lista salas com paginação e filtros"""
    resultado = service.get_by_query(filtros)
    return RespostaPaginada(dados=resultado.items, paginacao=resultado.paginacao)


@router.get("/{sala_id}", response_model=RespostaDados[SalaResponseDetalhada])
@inject
def obter_sala(
    sala_id: UUID,
    service: SalaService = Depends(Provide[Container.sala_service]),
):
    """Obtém uma sala pelo ID"""
    sala = service.get_by_id(sala_id)
    return RespostaDados(dados=sala)


@router.get("/bloco/{bloco_id}", response_model=RespostaLista[SalaResponse])
@inject
def listar_salas_por_bloco(
    bloco_id: UUID,
    service: SalaService = Depends(Provide[Container.sala_service]),
):
    """Lista todas as salas de um bloco"""
    salas = service.get_by_bloco(bloco_id)
    return RespostaLista(dados=salas)


@router.post("", response_model=RespostaDados[SalaResponse])
@inject
async def criar_sala(
    sala: SalaCreate,
    service: SalaService = Depends(Provide[Container.sala_service]),
):
    """Cria uma nova sala"""
    dados = service.create(sala)
    return RespostaDados(dados=dados)


@router.patch("/{sala_id}", response_model=RespostaDados[SalaResponse])
@inject
def atualizar_sala(
    sala_id: UUID,
    sala: SalaUpdate,
    service: SalaService = Depends(Provide[Container.sala_service]),
):
    """Atualiza uma sala existente"""
    return RespostaDados(dados=service.update(sala_id, sala))


@router.delete("/{sala_id}", response_model=RespostaDados[SalaResponse])
@inject
def remover_sala(
    sala_id: UUID,
    service: SalaService = Depends(Provide[Container.sala_service]),
):
    """Remove uma sala"""
    return RespostaDados(dados=service.delete(sala_id))
