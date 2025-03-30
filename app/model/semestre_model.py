from sqlalchemy import Column, String, Boolean, Date
from app.model.base_model import BaseModel
import uuid
from sqlalchemy.dialects.postgresql import UUID


class Semestre(BaseModel):
    """
    Modelo para semestres.
    """

    __tablename__ = "semestres"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    identificador = Column(
        String(12),
        nullable=False,
        comment="Identificador do semestre no formato '2025.1'",
        unique=True,
    )
    data_inicio = Column(Date, nullable=False, comment="Data de início do semestre")
    data_fim = Column(Date, nullable=False, comment="Data de fim do semestre")
    ativo = Column(
        Boolean, nullable=False, default=True, comment="Indica se o semestre está ativo"
    )
