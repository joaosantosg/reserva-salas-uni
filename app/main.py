from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.core.di.container import Container

from app.api.v1.auth_api import router as auth_router
from app.api.v1.usuario_api import router as usuario_router
from app.api.v1.reserva_api import router as reserva_router
from app.api.v1.bloco_api import router as bloco_router
from app.api.v1.sala_api import router as sala_router
from app.api.v1.semestre_api import router as semestre_router
from app.api.v1.relatorio_api import router as relatorio_router
from app.core.config.settings import settings
from app.core.config.logging import setup_logging
from app.core.database.database import init_db
from app.core.commons.exceptions import BaseAPIException, api_exception_handler
import logging

logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    # Create container
    container = Container()

    # Wire the container to your modules
    container.wire(packages=["app.api.v1"])

    app = FastAPI(
        title="Reserva Salas UNI",
        version="0.1.0",
        openapi_tags=[
            {
                "name": "auth",
                "description": "Operações de autenticação",
            },
            {
                "name": "relatorios",
                "description": "Relatórios e estatísticas",
            },
        ],
        swagger_ui_parameters={
            "persistAuthorization": True,
        },
        swagger_ui_init_oauth={
            "usePkceWithAuthorizationCodeGrant": True,
        },
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Setup logging
    setup_logging()

    # Initialize database
    init_db()

    # Register exception handlers
    app.add_exception_handler(BaseAPIException, api_exception_handler)

    # Adicione a configuração de segurança global
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title="Reserva Salas UNI",
            version="0.1.0",
            description="API para sistema de reserva de salas",
            routes=app.routes,
        )

        # Adiciona o componente de segurança
        openapi_schema["components"]["securitySchemes"] = {
            "JWT": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Enter JWT Bearer token",
            }
        }

        # Aplica segurança globalmente
        openapi_schema["security"] = [{"JWT": []}]

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

    # Root endpoint
    @app.get("/")
    def root():
        return "service is working"

    # Include routers
    app.include_router(auth_router, prefix=settings.API_V1_STR)
    app.include_router(usuario_router, prefix=settings.API_V1_STR)
    app.include_router(reserva_router, prefix=settings.API_V1_STR)
    app.include_router(bloco_router, prefix=settings.API_V1_STR)
    app.include_router(sala_router, prefix=settings.API_V1_STR)
    app.include_router(semestre_router, prefix=settings.API_V1_STR)
    app.include_router(relatorio_router, prefix=settings.API_V1_STR)

    # Start scheduler
    @app.on_event("startup")
    async def startup_event():
        scheduler_service = container.scheduler_service()
        scheduler_service.start()
        scheduler_service.schedule_daily_notifications()
        logger.info("Scheduler started and daily notifications scheduled")

    # Stop scheduler
    @app.on_event("shutdown")
    async def shutdown_event():
        scheduler_service = container.scheduler_service()
        scheduler_service.stop()
        logger.info("Scheduler stopped")

    return app

app = create_app()
