from typing import Generator
import logging
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config.settings import settings
from app.model.base_model import Base

# Configure logging
logger = logging.getLogger(__name__)



# Create engine for PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG,
    pool_size=5,
    max_overflow=10,
    connect_args={
        "connect_timeout": 10,
        "application_name": settings.PROJECT_NAME
    }
)

# Create session factory - exposed for DI container
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

class Database:
    """Classe para gerenciar conexões do banco de dados"""
    
    def __init__(self, db_url: str):
        self.engine = create_engine(
            db_url,
            pool_pre_ping=True,
            echo=settings.DEBUG,
            pool_size=5,
            max_overflow=10,
            connect_args={
                "connect_timeout": 10,
                "application_name": settings.PROJECT_NAME
            }
        )
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False
        )

    def create_database(self) -> None:
        """Cria todas as tabelas no banco de dados"""
        Base.metadata.create_all(bind=self.engine)

    def get_session(self) -> Generator:
        """
        Retorna uma nova sessão do banco de dados
        
        Yields:
            Session: Sessão do SQLAlchemy
        """
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    @property
    def session(self):
        """Propriedade para compatibilidade com o container de DI"""
        return self.get_session()

def get_db() -> Generator:
    """
    Dependency para obter sessão do banco de dados
    
    Yields:
        Session: Sessão do SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    """
    Inicializa o banco de dados criando todas as tabelas
    Utiliza logging para registrar o processo de criação
    """
    logger.info("Iniciando criação das tabelas no banco de dados")
    
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    # Get all tables from metadata
    tables_to_create = Base.metadata.tables.keys()
    
    logger.info(f"Tabelas existentes: {', '.join(existing_tables) or 'Nenhuma'}")
    logger.info(f"Tabelas a serem criadas: {', '.join(tables_to_create)}")
    
    try:
        Base.metadata.create_all(bind=engine)
        
        # Verify which tables were actually created
        new_tables = set(inspector.get_table_names()) - set(existing_tables)
        if new_tables:
            logger.info(f"Tabelas criadas com sucesso: {', '.join(new_tables)}")
        else:
            logger.info("Nenhuma nova tabela precisou ser criada")

        # Verifica se Super User inicial foi criado
        ## Bscar com email admin@admin.com
        from app.repository.usuario_repository import UsuarioRepository
        from app.model.usuario_model import Usuario

        
        usuario_repository = UsuarioRepository(session=SessionLocal())
        usuario = usuario_repository.get_by_email("admin@admin.com")
        if not usuario:
            logger.info("Super User inicial não encontrado, criando...")
            usuario = Usuario(
                nome="Admin",
                email="admin@admin.com",
                curso="Engenharia de Software",
                matricula="1234567890",
                ativo=True,
                super_user=True
            )
            usuario.set_senha("admin")
            usuario_repository.save(usuario)
            logger.info("Super User inicial criado com sucesso")
            usuario_repository.session.commit()
            usuario_repository.session.refresh(usuario)
            logger.info(f"Super User inicial criado: {usuario.id}")
        else:
            logger.info(f"Super User inicial encontrado: {usuario.id}")
        
        logger.info("Inicialização do banco de dados concluída com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {str(e)}")
        raise 