from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide
from app.core.di.container import Container


from app.schema.auth_schema import LoginRequisicao, LoginResposta
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"],
)


@router.post("/login", response_model=LoginResposta)
@inject
def login(
    user_info: LoginRequisicao,
    service: AuthService = Depends(Provide[Container.auth_service]),
):
    return service.login(user_info)


# @router.get("/me", response_model=User)
# @inject
# def get_me(current_user: User = Depends(get_current_active_user)):
#     return current_user


# TODO: Implementar rotas de recuperação de senha e redefinição de senha

# TODO: Implementar rotas de refresh token
