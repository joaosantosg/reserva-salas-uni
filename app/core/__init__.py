# Import base components first
from app.core.config.settings import settings
from app.core.config.logging import logger

# Import database
from app.core.database.database import Base, get_db

# Import security
from app.core.security.jwt import JWTManager
from app.core.security.auth_dependencies import AuthDependencies

# Import middleware
from app.core.middleware.logging import LoggingMiddleware

# Import common utilities
from app.core.commons.responses import (
    RespostaBase,
    RespostaDados,
    RespostaPaginada,
    ParametrosPaginacao,
    InformacoesPaginacao,
)
from app.core.commons.exceptions import (
    BaseAPIException,
    NotFoundException,
    UnauthorizedException,
    ForbiddenException,
    ValidationException,
    ConflictException,
    BusinessException,
)
from app.core.commons.pagination import Paginator

# Import container last to avoid circular imports
from app.core.di.container import Container

__all__ = [
    "settings",
    "logger",
    "Base",
    "get_db",
    "JWTManager",
    "AuthDependencies",
    "LoggingMiddleware",
    "Container",
    "RespostaBase",
    "RespostaDados",
    "RespostaPaginada",
    "ParametrosPaginacao",
    "InformacoesPaginacao",
    "Paginator",
    "BaseAPIException",
    "NotFoundException",
    "UnauthorizedException",
    "ForbiddenException",
    "ValidationException",
    "ConflictException",
    "BusinessException",
]
