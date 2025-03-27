from sqlalchemy import Column, String, Boolean, DateTime, Integer
from app.model.base_model import BaseModel
from passlib.context import CryptContext
import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.util.datetime_utils import DateTimeUtils

# Configuração do bcrypt com maior segurança
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


class Usuario(BaseModel):
    """Modelo de usuário com recursos avançados de segurança e auditoria"""

    __tablename__ = "usuarios"

    # Campos de identificação
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="ID único do usuário",
    )
    nome = Column(String(255), nullable=False, comment="Nome completo do usuário")
    email = Column(
        String(255),
        nullable=False,
        unique=True,
        comment="Email institucional do usuário",
    )
    matricula = Column(
        String(20), nullable=False, unique=True, comment="Matrícula do Coordenador"
    )
    curso = Column(String(255), nullable=False, comment="Curso do usuário")

    # Campos de segurança
    senha = Column(String(255), nullable=False, comment="Hash da senha com bcrypt")

    # Campos de controle de acesso
    ativo = Column(
        Boolean, nullable=False, default=True, comment="Status de ativação da conta"
    )
    bloqueado = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Indica se a conta está bloqueada",
    )
    motivo_bloqueio = Column(
        String(255), nullable=True, comment="Motivo do bloqueio da conta"
    )
    tentativas_login = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Número de tentativas de login malsucedidas",
    )
    super_user = Column(
        Boolean, nullable=False, default=False, comment="Indica se é um super usuário"
    )

    # Campos de auditoria
    ultimo_login = Column(
        DateTime(timezone=True), nullable=True, comment="Data e hora do último login"
    )
    ultimo_ip = Column(String(45), nullable=True, comment="Último IP usado para login")
    criado_em = Column(
        DateTime(timezone=True),
        nullable=False,
        default=DateTimeUtils.now,
        comment="Data de criação",
    )
    atualizado_em = Column(
        DateTime(timezone=True),
        nullable=False,
        default=DateTimeUtils.now,
        onupdate=DateTimeUtils.now,
        comment="Data da última atualização",
    )

    def set_senha(self, senha: str) -> None:
        """Define a senha do usuário usando bcrypt (que já inclui o salt automaticamente)"""
        self.senha = pwd_context.hash(senha)
        self.tentativas_login = 0

    def verificar_senha(self, senha: str) -> bool:
        """Verifica se a senha fornecida corresponde ao hash armazenado"""
        return pwd_context.verify(senha, self.senha)

    def registrar_login(self, ip: str) -> None:
        """Registra um login bem-sucedido"""
        self.ultimo_login = DateTimeUtils.now()
        self.ultimo_ip = ip
        self.tentativas_login = 0
        if self.bloqueado:
            self.bloqueado = False
            self.motivo_bloqueio = None

    def registrar_tentativa_falha(self) -> None:
        """Registra uma tentativa de login malsucedida"""
        self.tentativas_login += 1
        if self.tentativas_login >= 5:
            self.bloqueado = True
            self.motivo_bloqueio = "Excesso de tentativas de login malsucedidas"

    def desativar(self, motivo: str) -> None:
        """Desativa a conta do usuário"""
        self.ativo = False
        self.bloqueado = True
        self.motivo_bloqueio = motivo

    def ativar(self) -> None:
        """Ativa a conta do usuário"""
        self.ativo = True
        self.bloqueado = False
        self.motivo_bloqueio = None
        self.tentativas_login = 0
