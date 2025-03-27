from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide
from uuid import UUID

from app.core.di.container import Container
from app.core.security.jwt import JWTManager
from app.core.commons.responses import RespostaDados, RespostaPaginada

from app.schema.bloco_schema import (
    BlocoFiltros, 
    BlocoResponse, 
    BlocoCreate, 
    BlocoUpdate
)
from app.services.bloco_service import BlocoService
from app.core.security.auth_dependencies import AuthDependencies

router = APIRouter(
    prefix="/bloco", 
    tags=["bloco"], 
    dependencies=[Depends(AuthDependencies.get_current_active_superuser)]
)

@router.get("", response_model=RespostaPaginada[BlocoResponse])
@inject
def listar_blocos(
    filtros: BlocoFiltros = Depends(),
    service: BlocoService = Depends(Provide[Container.bloco_service]),
):
    """Lista blocos com paginação e filtros"""
    resultado = service.get_by_query(filtros)
    return RespostaPaginada(
        dados=resultado.items,
        paginacao=resultado.paginacao
    )

@router.get("/{bloco_id}", response_model=RespostaDados[BlocoResponse])
@inject
def obter_bloco(
    bloco_id: UUID,
    service: BlocoService = Depends(Provide[Container.bloco_service]),
):
    """Obtém um bloco pelo ID"""
    bloco = service.get_by_id(bloco_id)
    return RespostaDados(dados=bloco)

@router.post("", response_model=RespostaDados[BlocoResponse])
@inject
async def criar_bloco(
    bloco: BlocoCreate,
    service: BlocoService = Depends(Provide[Container.bloco_service]),
):
    """Cria um novo bloco"""
    dados = service.create(bloco)
    return RespostaDados(dados=dados)

@router.patch("/{bloco_id}", response_model=RespostaDados[BlocoResponse])
@inject
def atualizar_bloco(
    bloco_id: UUID,
    bloco: BlocoUpdate,
    service: BlocoService = Depends(Provide[Container.bloco_service]),
):
    """Atualiza um bloco existente"""
    return RespostaDados(dados=service.update(bloco_id, bloco))

@router.delete("/{bloco_id}", response_model=RespostaDados[BlocoResponse])
@inject
def remover_bloco(
    bloco_id: UUID,
    service: BlocoService = Depends(Provide[Container.bloco_service]),
):
    """Remove um bloco"""
    return RespostaDados(dados=service.delete(bloco_id)) 