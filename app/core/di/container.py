from dependency_injector import containers, providers

from app.core.database.database import SessionLocal
from app.repository.usuario_repository import UsuarioRepository
from app.repository.reserva_repository import ReservaRepository
from app.repository.reserva_recorrente_repository import ReservaRecorrenteRepository
from app.repository.bloco_repository import BlocoRepository
from app.repository.sala_repository import SalaRepository
from app.repository.auditoria_repository import AuditoriaRepository
from app.repository.semestre_repository import SemestreRepository
from app.services.usuario_service import UsuarioService
from app.services.reserva_service import ReservaService
from app.services.reserva_recorrente_service import ReservaRecorrenteService
from app.services.semestre_service import SemestreService
from app.services.bloco_service import BlocoService
from app.services.sala_service import SalaService
from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from app.services.auditoria_service import AuditoriaService
from app.core.security.jwt import JWTManager
from app.clients.email_client import EmailClient


class Container(containers.DeclarativeContainer):
    """Container de injeção de dependência"""

    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.api.v1.auth_api",
            "app.api.v1.usuario_api",
            "app.api.v1.reserva_api",
            "app.api.v1.bloco_api",
            "app.api.v1.sala_api",
            "app.api.v1.semestre_api",
        ],
        packages=["app.api.v1"],
    )

    # Database
    db = providers.Singleton(SessionLocal)

    # Clients
    email_client = providers.Singleton(EmailClient)

    # Repositories
    usuario_repository = providers.Factory(UsuarioRepository, session=db)
    reserva_repository = providers.Factory(ReservaRepository, session=db)
    reserva_recorrente_repository = providers.Factory(
        ReservaRecorrenteRepository, session=db
    )
    bloco_repository = providers.Factory(BlocoRepository, session=db)
    sala_repository = providers.Factory(SalaRepository, session=db)
    auditoria_repository = providers.Factory(AuditoriaRepository, session=db)
    semestre_repository = providers.Factory(SemestreRepository, session=db)
    # Services
    email_service = providers.Factory(EmailService, email_client=email_client)
    auditoria_service = providers.Factory(
        AuditoriaService, auditoria_repository=auditoria_repository
    )

    usuario_service = providers.Factory(
        UsuarioService, usuario_repository=usuario_repository
    )
    semestre_service = providers.Factory(
        SemestreService, semestre_repository=semestre_repository
    )
    
    reserva_service = providers.Factory(
        ReservaService,
        reserva_repository=reserva_repository,
        sala_repository=sala_repository,
        usuario_repository=usuario_repository,
        email_service=email_service,
        auditoria_service=auditoria_service,
    )


    reserva_recorrente_service = providers.Factory(
        ReservaRecorrenteService,
        reserva_repository=reserva_repository,
        reserva_recorrente_repository=reserva_recorrente_repository,
        sala_repository=sala_repository,
        usuario_repository=usuario_repository,
        email_service=email_service,
        auditoria_service=auditoria_service,
        semestre_service=semestre_service,
    )

    bloco_service = providers.Factory(BlocoService, bloco_repository=bloco_repository)

    sala_service = providers.Factory(
        SalaService, sala_repository=sala_repository, bloco_repository=bloco_repository
    )

    auth_service = providers.Factory(AuthService, user_repository=usuario_repository)



    # Security
    jwt_manager = providers.Singleton(JWTManager)
