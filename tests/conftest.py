import json
import os

import pytest
from datetime import datetime, date, time, timedelta
from uuid import UUID, uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["ENV"] = "test"

if os.getenv("ENV") not in ["test"]:
    msg = f"ENV is not test, it is {os.getenv('ENV')}"
    pytest.exit(msg)

from fastapi.testclient import TestClient
from loguru import logger

from app.core.config.settings import settings
from app.core.di.container import Container
from app.core.database.database import Base
from app.model.usuario_model import Usuario
from app.model.sala_model import Sala
from app.model.bloco_model import Bloco
from app.model.reserva_model import Reserva
from app.model.reserva_recorrente_model import ReservaRecorrente
from app.schema.reserva_schema import FrequenciaRecorrencia
from app.services.email_service import EmailService
from app.repository.reserva_repository import ReservaRepository
from app.repository.reserva_recorrente_repository import ReservaRecorrenteRepository
from app.repository.sala_repository import SalaRepository
from app.repository.usuario_repository import UsuarioRepository
from app.core.security.jwt import JWTManager
from app.main import create_app

# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(engine):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture
def usuario(db_session) -> Usuario:
    usuario = Usuario(
        id=uuid4(),
        nome="Teste",
        email="teste@teste.com",
        matricula="123456",
        senha="senha123",
        ativo=True
    )
    db_session.add(usuario)
    db_session.commit()

    # Gerar token JWT
    jwt_manager = JWTManager()
    token = jwt_manager.create_access_token(usuario.id)
    usuario.token = token
    
    return usuario

@pytest.fixture
def bloco(db_session) -> Bloco:
    bloco = Bloco(
        id=uuid4(),
        nome="Bloco A",
        ativo=True
    )
    db_session.add(bloco)
    db_session.commit()
    return bloco

@pytest.fixture
def sala(db_session, bloco) -> Sala:
    sala = Sala(
        id=uuid4(),
        numero="101",
        capacidade=40,
        bloco_id=bloco.id,
        ativo=True
    )
    db_session.add(sala)
    db_session.commit()
    return sala

@pytest.fixture
def reserva(db_session, sala, usuario) -> Reserva:
    reserva = Reserva(
        id=uuid4(),
        sala_id=sala.id,
        usuario_id=usuario.id,
        inicio=datetime.now() + timedelta(days=1),
        fim=datetime.now() + timedelta(days=1, hours=2),
        motivo="Teste",
        ativo=True
    )
    db_session.add(reserva)
    db_session.commit()
    return reserva

@pytest.fixture
def reserva_recorrente(db_session, sala, usuario) -> ReservaRecorrente:
    reserva = ReservaRecorrente(
        id=uuid4(),
        sala_id=sala.id,
        usuario_id=usuario.id,
        data_inicio=date.today() + timedelta(days=1),
        data_fim=date.today() + timedelta(days=30),
        hora_inicio=time(8, 0),
        hora_fim=time(10, 0),
        frequencia=FrequenciaRecorrencia.SEMANAL,
        dia_da_semana=[0, 2, 4],  # Segunda, Quarta, Sexta
        motivo="Aula de Teste",
        ativo=True
    )
    db_session.add(reserva)
    db_session.commit()
    return reserva

@pytest.fixture
def email_service():
    return EmailService()

@pytest.fixture
def reserva_repository(db_session):
    return ReservaRepository(db_session)

@pytest.fixture
def reserva_recorrente_repository(db_session):
    return ReservaRecorrenteRepository(db_session)

@pytest.fixture
def sala_repository(db_session):
    return SalaRepository(db_session)

@pytest.fixture
def usuario_repository(db_session):
    return UsuarioRepository(db_session)


def reset_db():
    engine = create_engine(settings.DATABASE_URI)
    logger.info(engine)
    with engine.begin() as conn:
        if "test" in settings.DATABASE_URI:
            from app.model.base_model import Base
            Base.metadata.drop_all(conn)
            Base.metadata.create_all(conn)
        else:
            raise Exception("Not in test environment")
    return engine


@pytest.fixture
def client():
    reset_db()
    app = create_app()
    with TestClient(app) as client:
        yield client


@pytest.fixture
def container():
    return Container()


@pytest.fixture
def test_name(request):
    return request.node.name
