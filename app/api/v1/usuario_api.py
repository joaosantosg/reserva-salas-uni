from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide
from uuid import UUID

from app.core.di.container import Container
from app.core.commons.responses import RespostaDados, RespostaPaginada

from app.schema.usuario_schema import (
    UsuarioFiltros,
    UsuarioResponse,
    UsuarioCreate,
    UsuarioUpdate,
)
from app.services.usuario_service import UsuarioService
from app.core.security.auth_dependencies import AuthDependencies

router = APIRouter(
    prefix="/usuario",
    tags=["Usuários"],
    dependencies=[Depends(AuthDependencies.get_current_active_superuser)],
)


@router.get("", response_model=RespostaPaginada[UsuarioResponse])
@inject
def listar_usuarios(
    filtros: UsuarioFiltros = Depends(),
    service: UsuarioService = Depends(Provide[Container.usuario_service]),
):
    resultado = service.get_by_query(filtros)
    return RespostaPaginada(dados=resultado.items, paginacao=resultado.paginacao)


@router.get("/{usuario_id}", response_model=RespostaDados[UsuarioResponse])
@inject
def obter_usuario(
    usuario_id: UUID,
    service: UsuarioService = Depends(Provide[Container.usuario_service]),
):
    usuario = service.get_by_id(usuario_id)
    return RespostaDados(dados=usuario)


@router.post("", response_model=RespostaDados[UsuarioResponse])
@inject
async def criar_usuario(
    usuario: UsuarioCreate,
    service: UsuarioService = Depends(Provide[Container.usuario_service]),
):
    dados = service.create(usuario)
    return RespostaDados(dados=dados)


@router.patch("/{usuario_id}", response_model=RespostaDados[UsuarioResponse])
@inject
def atualizar_usuario(
    usuario_id: UUID,
    usuario: UsuarioUpdate,
    service: UsuarioService = Depends(Provide[Container.usuario_service]),
):
    return RespostaDados(dados=service.update(usuario_id, usuario))


@router.delete("/{usuario_id}", response_model=RespostaDados[UsuarioResponse])
@inject
def remover_usuario(
    usuario_id: UUID,
    service: UsuarioService = Depends(Provide[Container.usuario_service]),
):
    return RespostaDados(dados=service.delete(usuario_id))
