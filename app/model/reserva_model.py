from sqlalchemy import Column, DateTime, ForeignKey, Text, CheckConstraint
from sqlalchemy.orm import relationship
from app.model.base_model import BaseModel
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.util.datetime_utils import DateTimeUtils

class Reserva(BaseModel):
    __tablename__ = "reservas"
    __table_args__ = (
        CheckConstraint('inicio < fim', name="ck_reserva_periodo_valido"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sala_id = Column(UUID(as_uuid=True), ForeignKey("salas.id", ondelete="CASCADE"), nullable=False)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    inicio = Column(DateTime(timezone=True), nullable=False)
    fim = Column(DateTime(timezone=True), nullable=False)
    motivo = Column(Text)
    reserva_recorrente_id = Column(UUID(as_uuid=True), ForeignKey("reservas_recorrentes.id", ondelete="CASCADE"), nullable=True)
    criado_em = Column(DateTime(timezone=True), nullable=False, default=DateTimeUtils.now)
    atualizado_em = Column(DateTime(timezone=True), nullable=False, default=DateTimeUtils.now, onupdate=DateTimeUtils.now)
    excluido_em = Column(DateTime(timezone=True), nullable=True)
    excluido_por_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)

    # Relationships
    sala = relationship("Sala")
    usuario = relationship("Usuario", foreign_keys=[usuario_id])
    reserva_recorrente = relationship("ReservaRecorrente")

    def __repr__(self):
        return f"<Reserva(id={self.id}, sala_id={self.sala_id}, inicio={self.inicio}, fim={self.fim})>"