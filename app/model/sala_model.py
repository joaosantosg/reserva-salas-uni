from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    ForeignKey,
    UniqueConstraint,
    ARRAY,
    Text,
    DateTime,
)
from sqlalchemy.orm import relationship
from app.model.base_model import BaseModel
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.util.datetime_utils import DateTimeUtils


class Sala(BaseModel):
    __tablename__ = "salas"
    __table_args__ = (
        UniqueConstraint("bloco_id", "identificacao_sala", name="uq_sala_por_bloco"),
    )

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="ID da sala"
    )
    bloco_id = Column(
        UUID(as_uuid=True),
        ForeignKey("blocos.id", ondelete="CASCADE"),
        nullable=False,
        comment="ID do bloco",
    )
    identificacao_sala = Column(
        String(20), nullable=False, comment="Identificação da sala"
    )
    capacidade_maxima = Column(
        Integer, nullable=False, comment="Capacidade máxima da sala"
    )
    recursos = Column(ARRAY(Text), default=[], comment="Recursos disponíveis na sala")
    uso_restrito = Column(
        Boolean, default=False, comment="Indica se a sala é restrita para uso"
    )
    curso_restrito = Column(
        String(100), nullable=True, comment="Curso restrito para uso da sala"
    )
    criado_em = Column(
        DateTime(timezone=True), nullable=False, default=DateTimeUtils.now
    )
    atualizado_em = Column(
        DateTime(timezone=True),
        nullable=False,
        default=DateTimeUtils.now,
        onupdate=DateTimeUtils.now,
    )

    bloco = relationship("Bloco", backref="salas")
