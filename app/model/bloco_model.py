from sqlalchemy import Column, String, DateTime
from app.util.datetime_utils import DateTimeUtils
from app.model.base_model import BaseModel
import uuid
from sqlalchemy.dialects.postgresql import UUID


class Bloco(BaseModel):
    __tablename__ = "blocos"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="ID do bloco"
    )
    nome = Column(String(100), nullable=False, comment="Nome do bloco")
    identificacao = Column(
        String(20), nullable=False, unique=True, comment="Identificação do bloco"
    )
    criado_em = Column(
        DateTime, default=DateTimeUtils.now, comment="Data de criação do bloco"
    )
    atualizado_em = Column(
        DateTime,
        default=DateTimeUtils.now,
        onupdate=DateTimeUtils.now,
        comment="Data de atualização do bloco",
    )
