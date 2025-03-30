from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Enum,
    Time,
    Date,
    Text,
    ARRAY,
    DateTime,
    Boolean,
    String,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from app.model.base_model import BaseModel
import enum
import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.util.datetime_utils import DateTimeUtils
from datetime import datetime, date, time
from typing import List, Optional


class FrequenciaEnum(str, enum.Enum):
    DIARIO = "DIARIO"
    SEMANAL = "SEMANAL"
    MENSAL = "MENSAL"

    @classmethod
    def get_display_name(cls, value: str) -> str:
        """Retorna o nome de exibição da frequência"""
        display_names = {
            "DIARIO": "Diária",
            "SEMANAL": "Semanal",
            "MENSAL": "Mensal"
        }
        return display_names.get(value, value)


class TipoReservaRecorrente(str, enum.Enum):
    REGULAR = "REGULAR"
    SEMESTRE = "SEMESTRE"

    @classmethod
    def get_display_name(cls, value: str) -> str:
        """Retorna o nome de exibição do tipo"""
        display_names = {
            "REGULAR": "Regular",
            "SEMESTRE": "Semestre"
        }
        return display_names.get(value, value)


class ReservaRecorrente(BaseModel):
    __tablename__ = "reservas_recorrentes"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="ID da reserva recorrente",
    )
    identificacao = Column(
        String(255), 
        nullable=True, 
        comment="Identificação da reserva recorrente, no formato 'DIARIO-SALA101-14H'"
    )
    tipo = Column(
        Enum(TipoReservaRecorrente), 
        nullable=False, 
        comment="Tipo de reserva recorrente: REGULAR ou SEMESTRE"
    )
    motivo = Column(Text, comment="Motivo da reserva recorrente")
    sala_id = Column(
        UUID(as_uuid=True),
        ForeignKey("salas.id", ondelete="CASCADE"),
        nullable=False,
        comment="ID da sala",
    )
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id"),
        nullable=False,
        comment="ID do usuario responsavel pela reserva recorrente",
    )
    frequencia = Column(
        Enum(FrequenciaEnum), 
        nullable=False, 
        comment="Frequência da reserva recorrente, DIARIO, SEMANAL ou MENSAL"
    )
    dia_da_semana = Column(
        ARRAY(Integer), 
        nullable=True, 
        comment="Dia da semana (0=segunda, 6=domingo), Apenas para frequência SEMANAL"
    )
    dia_do_mes = Column(
        Integer, 
        nullable=True, 
        comment="Dia do mês (1-31), Apenas para frequência MENSAL"
    )
    hora_inicio = Column(
        Time, 
        nullable=False, 
        comment="Hora de início da reserva recorrente"
    )
    hora_fim = Column(
        Time, 
        nullable=False, 
        comment="Hora de fim da reserva recorrente"
    )
    data_inicio = Column(
        Date, 
        nullable=False, 
        comment="Data de início da reserva recorrente"
    )
    data_fim = Column(
        Date, 
        nullable=False, 
        comment="Data de fim da reserva recorrente"
    )
    excecoes = Column(
        ARRAY(Date), 
        default=[], 
        comment="Exceções da reserva recorrente"
    )
    semestre = Column(
        String(12), 
        nullable=True, 
        comment="Semestre da reserva recorrente, no formato '2025.1'"
    )
    criado_em = Column(
        DateTime(), 
        nullable=False, 
        default=DateTimeUtils.now
    )
    atualizado_em = Column(
        DateTime(),
        nullable=False,
        default=DateTimeUtils.now,
        onupdate=DateTimeUtils.now,
    )
    excluido_em = Column(DateTime(timezone=True), nullable=True)
    excluido_por_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("usuarios.id"), 
        nullable=True
    )

    # Relationships
    sala = relationship("Sala")
    usuario = relationship("Usuario", foreign_keys=[usuario_id])


    # Constraints
    __table_args__ = (
        CheckConstraint('hora_fim > hora_inicio', name='check_hora_fim_maior_inicio'),
        CheckConstraint('data_fim >= data_inicio', name='check_data_fim_maior_inicio'),
    )

    @property
    def duracao_minutos(self) -> int:
        """Retorna a duração da reserva em minutos"""
        inicio = datetime.combine(date.today(), self.hora_inicio)
        fim = datetime.combine(date.today(), self.hora_fim)
        return int((fim - inicio).total_seconds() / 60)

    @property
    def dias_semana_nomes(self) -> List[str]:
        """Retorna os nomes dos dias da semana selecionados"""
        if not self.dia_da_semana:
            return []
        nomes = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
        return [nomes[dia] for dia in sorted(self.dia_da_semana)]

    @property
    def frequencia_display(self) -> str:
        """Retorna o nome de exibição da frequência"""
        return FrequenciaEnum.get_display_name(self.frequencia)

    @property
    def tipo_display(self) -> str:
        """Retorna o nome de exibição do tipo"""
        return TipoReservaRecorrente.get_display_name(self.tipo)

    @property
    def horario_formatado(self) -> str:
        """Retorna o horário formatado"""
        return f"{self.hora_inicio.strftime('%H:%M')} - {self.hora_fim.strftime('%H:%M')}"

    @property
    def periodo_formatado(self) -> str:
        """Retorna o período formatado"""
        return f"{self.data_inicio.strftime('%d/%m/%Y')} a {self.data_fim.strftime('%d/%m/%Y')}"

    def is_ativo(self) -> bool:
        """Verifica se a reserva está ativa"""
        hoje = date.today()
        return (
            not self.excluido_em
            and self.data_inicio <= hoje <= self.data_fim
        )

    def is_excecao(self, data: date) -> bool:
        """Verifica se uma data é uma exceção"""
        if not self.excecoes:
            return False
        return data in self.excecoes

    def __repr__(self) -> str:
        """Representação string da reserva recorrente"""
        return (
            f"<ReservaRecorrente("
            f"id={self.id}, "
            f"identificacao={self.identificacao}, "
            f"tipo={self.tipo_display}, "
            f"frequencia={self.frequencia_display}, "
            f"sala_id={self.sala_id}, "
            f"periodo={self.periodo_formatado}"
            f")>"
        )


