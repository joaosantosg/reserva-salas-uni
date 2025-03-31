from typing import Generator, Optional
import logging
from contextlib import contextmanager
from sqlalchemy import create_engine, inspect, event
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from app.core.config.settings import settings
from app.model.base_model import Base

# Configure logging
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Classe para gerenciar conexões do banco de dados"""

    def __init__(self, db_url: str):
        if not db_url:
            raise ValueError("DATABASE_URL não pode estar vazio")

        self.engine = create_engine(
            db_url,
            pool_pre_ping=True,
            pool_size=5,
            connect_args={"connect_timeout": 10}
        )
        
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        )

    def create_database(self) -> None:
        """Cria todas as tabelas no banco de dados"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Tabelas criadas com sucesso")
        except SQLAlchemyError as e:
            logger.error(f"Erro ao criar tabelas: {str(e)}")
            raise

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Context manager para gerenciar sessões do banco de dados.
        Garante que a sessão seja fechada mesmo em caso de erro.
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Erro na operação do banco: {str(e)}")
            raise
        finally:
            session.close()

    def execute_in_session(self, operation):
        """
        Executa uma operação dentro de uma sessão do banco de dados.
        Gerencia automaticamente commit/rollback.
        """
        with self.get_session() as session:
            try:
                return operation(session)
            except OperationalError as e:
                logger.error(f"Erro de operação no banco: {str(e)}")
                raise
            except SQLAlchemyError as e:
                logger.error(f"Erro SQLAlchemy: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"Erro inesperado: {str(e)}")
                raise

    def close_all_sessions(self):
        """Fecha todas as sessões ativas"""
        self.SessionLocal.remove()

    @property
    def session(self):
        """Propriedade para compatibilidade com o container de DI"""
        return self.get_session()


# Create a global instance of DatabaseManager
db_manager = DatabaseManager(settings.DATABASE_URL)

# Export SessionLocal for dependency injection
SessionLocal = db_manager.SessionLocal

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Inicializa o banco de dados criando todas as tabelas.
    Utiliza logging para registrar o processo de criação.
    """
    logger.info("Iniciando criação das tabelas no banco de dados")

    inspector = inspect(DatabaseManager(settings.DATABASE_URL).engine)
    existing_tables = inspector.get_table_names()
    tables_to_create = Base.metadata.tables.keys()

    logger.info(f"Tabelas existentes: {', '.join(existing_tables) or 'Nenhuma'}")
    logger.info(f"Tabelas a serem criadas: {', '.join(tables_to_create)}")

    try:
        db_manager.create_database()
        logger.info("Database initialized successfully")

        # Verifica se Super User inicial foi criado
        def create_super_user(session):
            from app.repository.usuario_repository import UsuarioRepository
            from app.model.usuario_model import Usuario

            usuario_repository = UsuarioRepository(session=session)
            usuario = usuario_repository.get_by_email("admin@admin.com")
            
            if not usuario:
                logger.info("Super User inicial não encontrado, criando...")
                usuario = Usuario(
                    nome="Admin",
                    email="admin@admin.com",
                    curso="Engenharia de Software",
                    matricula="1234567890",
                    ativo=True,
                    super_user=True,
                )
                usuario.set_senha("admin")
                
                usuario = usuario_repository.save(usuario)
                logger.info(f"Super User inicial criado: {usuario.id}")
            else:
                logger.info(f"Super User inicial encontrado: {usuario.id}")

        db_manager.execute_in_session(create_super_user)
        logger.info("Inicialização do banco de dados concluída com sucesso")

    except SQLAlchemyError as e:
        logger.error(f"Database initialization error: {e}")
        raise
