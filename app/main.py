from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.core.di.container import Container

from app.api.v1.auth_api import router as auth_router
from app.api.v1.usuario_api import router as usuario_router
from app.api.v1.reserva_api import router as reserva_router
from app.api.v1.bloco_api import router as bloco_router
from app.api.v1.sala_api import router as sala_router
from app.core.config.settings import settings
from app.core.config.logging import setup_logging
from app.core.database.database import init_db
from app.core.commons.exceptions import BaseAPIException, api_exception_handler
from app.scripts.processar_reservas_recorrentes import processar_reservas

def create_app() -> FastAPI:
    # Create container
    container = Container()
    
    # Wire the container to your modules
    container.wire(packages=["app.api.v1"])
    
    app = FastAPI(
        title="Reserva Salas UNI",
        version="0.0.1",
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
    # init_db()

    # Register exception handlers
    app.add_exception_handler(BaseAPIException, api_exception_handler)


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
    return app

app = create_app()
