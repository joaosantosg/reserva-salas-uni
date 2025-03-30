from fastapi import APIRouter, Depends
from app.core.security.auth_dependencies import AuthDependencies

router = APIRouter(
    prefix="/relatorio",
    tags=["Relatórios"],
    dependencies=[Depends(AuthDependencies.get_current_user)],
)

# @router.get("/uso-salas", response_model=RelatorioUsoSalas)
# async def gerar_relatorio_uso_salas(
#     data_inicio: datetime = Query(..., description="Data inicial do relatório"),
#     data_fim: datetime = Query(..., description="Data final do relatório"),
#     reserva_repository: ReservaRepository = Depends(),
#     current_user: Usuario = Depends(AuthDependencies.get_current_active_superuser)
# ):
#     """
#     Gera relatório com estatísticas de uso das salas.
#     Requer privilégios de superusuário.
#     """
#     relatorio_service = RelatorioService(reserva_repository)
#     return relatorio_service.gerar_relatorio_uso_salas(data_inicio, data_fim)
