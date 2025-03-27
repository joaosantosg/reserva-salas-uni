from typing import Any, Dict, Optional
from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse
from datetime import datetime


class BaseAPIException(HTTPException):
    """Exceção base para todas as exceções da API"""

    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        error_response = {
            "status": "erro",
            "mensagem": detail,
            "data_hora": datetime.now().isoformat(),
            "codigo": status_code,
        }
        super().__init__(
            status_code=status_code, detail=error_response, headers=headers
        )

    def __str__(self) -> str:
        """Retorna a mensagem de erro formatada"""
        return self.detail["mensagem"]


async def api_exception_handler(
    request: Request, exc: BaseAPIException
) -> JSONResponse:
    """Handler para exceções da API"""
    return JSONResponse(
        status_code=exc.status_code, content=exc.detail, headers=exc.headers
    )


class NotFoundException(BaseAPIException):
    """Exceção para recursos não encontrados"""

    def __init__(self, mensagem: str = "Recurso não encontrado") -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=mensagem)


class UnauthorizedException(BaseAPIException):
    """Exceção para usuários não autorizados"""

    def __init__(self, mensagem: str = "Não autorizado") -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=mensagem)


class ForbiddenException(BaseAPIException):
    """Exceção para acesso negado"""

    def __init__(self, mensagem: str = "Acesso negado") -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=mensagem)


class ValidationException(BaseAPIException):
    """Exceção para erros de validação"""

    def __init__(self, mensagem: str = "Erro de validação") -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=mensagem
        )


class ConflictException(BaseAPIException):
    """Exceção para conflitos de dados"""

    def __init__(self, mensagem: str = "Conflito de dados") -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=mensagem)


class BusinessException(BaseAPIException):
    """Exceção para regras de negócio"""

    def __init__(self, mensagem: str) -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=mensagem)


class AuthException(BaseAPIException):
    """Exceção para erros de autenticação"""

    def __init__(self, mensagem: str = "Erro de autenticação") -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=mensagem)


class DuplicatedException(BaseAPIException):
    """Exceção para erros de duplicação"""

    def __init__(self, mensagem: str = "Erro de duplicação") -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=mensagem)
