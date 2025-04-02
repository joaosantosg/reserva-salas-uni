from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide
from uuid import UUID
from app.core.di.container import Container
from app.core.commons.responses import RespostaDados, RespostaLista

from app.schema.semestre_schema import (
    SemestreResponse,
    SemestreCreate,
)
from app.services.semestre_service import SemestreService
from app.core.security.auth_dependencies import AuthDependencies

router = APIRouter(
    prefix="/semestre",
    tags=["Semestres"],
    dependencies=[Depends(AuthDependencies.get_current_user)],
)


@router.get("", response_model=RespostaLista[SemestreResponse], dependencies=[Depends(AuthDependencies.get_current_user)])
@inject
def listar_semestres(
    service: SemestreService = Depends(Provide[Container.semestre_service]),
):
    """Lista semestres"""
    resultado = service.get_all()
    return RespostaLista(dados=resultado)


@router.post("", response_model=RespostaDados[SemestreResponse], dependencies=[Depends(AuthDependencies.get_current_active_superuser)])
@inject
def criar_semestre(
    semestre: SemestreCreate,
    service: SemestreService = Depends(Provide[Container.semestre_service]),
):
    """Cria um semestre"""
    resultado = service.create(semestre)
    return RespostaDados(dados=resultado)


@router.get("/{semestre_id}", response_model=RespostaDados[SemestreResponse], dependencies=[Depends(AuthDependencies.get_current_active_superuser)])
@inject
def obter_semestre(semestre_id: UUID, service: SemestreService = Depends(Provide[Container.semestre_service]),
):
    """Obtém um semestre pelo ID"""
    resultado = service.get_by_id(semestre_id)
    return RespostaDados(dados=resultado)


@router.put("/{semestre_id}", response_model=RespostaDados[SemestreResponse], dependencies=[Depends(AuthDependencies.get_current_active_superuser)])
@inject
def atualizar_semestre(
    semestre_id: UUID,
    semestre: SemestreCreate,
    service: SemestreService = Depends(Provide[Container.semestre_service]),
):
    """Atualiza um semestre pelo ID"""
    resultado = service.update(semestre_id, semestre)
    return RespostaDados(dados=resultado)


@router.delete("/{semestre_id}", response_model=RespostaDados[SemestreResponse], dependencies=[Depends(AuthDependencies.get_current_active_superuser)])
@inject
def deletar_semestre(semestre_id: UUID, service: SemestreService = Depends(Provide[Container.semestre_service]),
):
    """Deleta um semestre pelo ID"""
    resultado = service.delete(semestre_id)
    return RespostaDados(dados=resultado)
