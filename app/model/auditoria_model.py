from sqlalchemy import Column, String, ForeignKey, JSON, DateTime, event
from sqlalchemy.orm import relationship
from app.model.base_model import BaseModel
from app.util.datetime_utils import DateTimeUtils
import uuid
from sqlalchemy.dialects.postgresql import UUID

class AuditoriaReserva(BaseModel):
    """
    Modelo para auditoria específica de reservas.
    Registra todas as operações realizadas em reservas e reservas recorrentes.
    Todas as datas são armazenadas em GMT-3 (São Paulo).
    """
    __tablename__ = "auditoria_reservas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="ID da auditoria")
    reserva_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("reservas.id", ondelete="SET NULL"), 
        nullable=True,
        comment="ID da reserva auditada (NULL se for reserva recorrente)"
    )
    reserva_recorrente_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("reservas_recorrentes.id", ondelete="SET NULL"), 
        nullable=True,
        comment="ID da reserva recorrente auditada (NULL se for reserva simples)"
    )
    acao = Column(
        String(20), 
        nullable=False, 
        comment="Tipo de operação: criar, atualizar, cancelar, confirmar"
    )
    dados_anteriores = Column(
        JSON, 
        comment="Estado anterior da reserva em formato JSON"
    )
    dados_novos = Column(
        JSON, 
        comment="Novo estado da reserva em formato JSON"
    )
    usuario_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("usuarios.id"), 
        nullable=False, 
        comment="ID do usuário que realizou a operação"
    )
    ip_address = Column(
        String(45), 
        comment="Endereço IP do usuário (suporte a IPv6)"
    )
    motivo = Column(
        String(255),
        nullable=True,
        comment="Motivo da operação (ex: cancelamento por conflito)"
    )
    criado_em = Column(
        DateTime(timezone=True),
        nullable=False,
        default=DateTimeUtils.now,
        comment="Data e hora da auditoria"
    )

    # Relacionamentos
    reserva = relationship("Reserva")
    reserva_recorrente = relationship("ReservaRecorrente")
    usuario = relationship("Usuario")

    def __repr__(self):
        return f"<AuditoriaReserva(id={self.id}, acao={self.acao})>"


def registrar_auditoria_reserva(mapper, connection, target):
    """
    Event listener para registrar mudanças em reservas.
    Acionado apenas para entidades Reserva e ReservaRecorrente.
    
    Args:
        mapper: Mapper SQLAlchemy da entidade
        connection: Conexão com o banco de dados
        target: Instância da reserva sendo modificada
    """
    if not hasattr(target, 'id'):
        return

    # Determina se é uma reserva simples ou recorrente
    is_recorrente = target.__tablename__ == 'reservas_recorrentes'
    
    auditoria = AuditoriaReserva(
        reserva_id=None if is_recorrente else target.id,
        reserva_recorrente_id=target.id if is_recorrente else None,
        acao='criar' if mapper.is_insert else 'atualizar',
        dados_novos=target.__dict__,
        dados_anteriores=mapper.old_state if mapper.old_state else None,
        usuario_id=target.usuario_id,  # Assume que a reserva tem usuario_id
        criado_em=DateTimeUtils.now()
    )
    connection.execute(auditoria.__table__.insert(), auditoria.__dict__)


def registrar_delete_reserva(mapper, connection, target):
    """
    Event listener para registrar cancelamentos de reservas.
    
    Args:
        mapper: Mapper SQLAlchemy da entidade
        connection: Conexão com o banco de dados
        target: Instância da reserva sendo cancelada
    """
    if not hasattr(target, 'id'):
        return

    is_recorrente = target.__tablename__ == 'reservas_recorrentes'
    
    auditoria = AuditoriaReserva(
        reserva_id=None if is_recorrente else target.id,
        reserva_recorrente_id=target.id if is_recorrente else None,
        acao='cancelar',
        dados_anteriores=target.__dict__,
        usuario_id=target.usuario_id,
        criado_em=DateTimeUtils.now()
    )
    connection.execute(auditoria.__table__.insert(), auditoria.__dict__)


def registrar_event_listeners_reserva():
    """
    Registra os event listeners apenas para as entidades de Reserva e ReservaRecorrente.
    Deve ser chamado na inicialização da aplicação.
    """
    from app.model.reserva_model import Reserva
    from app.model.reserva_recorrente_model import ReservaRecorrente

    for model in [Reserva, ReservaRecorrente]:
        event.listen(model, 'after_insert', registrar_auditoria_reserva)
        event.listen(model, 'after_update', registrar_auditoria_reserva)
        event.listen(model, 'after_delete', registrar_delete_reserva) 