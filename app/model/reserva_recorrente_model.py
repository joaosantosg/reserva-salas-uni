from sqlalchemy import Column, Integer, ForeignKey, Enum, Time, Date, Text, ARRAY, DateTime, String, Boolean
from sqlalchemy.orm import relationship
from app.model.base_model import BaseModel
import enum
import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.util.datetime_utils import DateTimeUtils


class FrequenciaEnum(str, enum.Enum):
    diaria = "DIARIA"
    semanal = "SEMANAL"
    mensal = "MENSAL"

class ReservaRecorrente(BaseModel):
    __tablename__ = "reservas_recorrentes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="ID da reserva recorrente")
    motivo = Column(Text, comment="Motivo da reserva recorrente")
    sala_id = Column(UUID(as_uuid=True), ForeignKey("salas.id", ondelete="CASCADE"), nullable=False, comment="ID da sala")
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False, comment="ID do usuario")
    frequencia = Column(Enum(FrequenciaEnum), nullable=False, comment="Frequência da reserva recorrente")
    dia_da_semana = Column(ARRAY(Integer), nullable=True, comment="Dia da semana (0=segunda, 6=domingo)")  # Apenas para frequência semanal
    dia_do_mes = Column(Integer, nullable=True, comment="Dia do mês (1-31)")  # Apenas para frequência mensal
    hora_inicio = Column(Time, nullable=False, comment="Hora de início da reserva recorrente")
    hora_fim = Column(Time, nullable=False, comment="Hora de fim da reserva recorrente")
    data_inicio = Column(Date, nullable=False, comment="Data de início da reserva recorrente")
    data_fim = Column(Date, nullable=False, comment="Data de fim da reserva recorrente")
    excecoes = Column(ARRAY(Date), default=[], comment="Exceções da reserva recorrente")
    ativo = Column(Boolean, default=True)

    semestre = Column(Integer, nullable=False)  # 1 ou 2
    ano = Column(Integer, nullable=False)
    criado_em = Column(DateTime(timezone=True), nullable=False, default=DateTimeUtils.now)
    atualizado_em = Column(DateTime(timezone=True), nullable=False, default=DateTimeUtils.now, onupdate=DateTimeUtils.now)
    excluido_em = Column(DateTime(timezone=True), nullable=True)
    excluido_por_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)

    # Relationships
    sala = relationship("Sala")
    usuario = relationship("Usuario", foreign_keys=[usuario_id])


    def __repr__(self):
        return f"<ReservaRecorrente(id={self.id}, identificacao={self.motivo}, sala_id={self.sala_id})>" 