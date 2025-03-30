from typing import List, Optional
from sqlalchemy.orm import Session
from app.repository.base_repository import BaseRepository
from app.model.auditoria_model import AuditoriaReserva
from app.util.datetime_utils import DateTimeUtils
import json


class AuditoriaRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session, AuditoriaReserva)

    def criar(
        self,
        reserva_id: Optional[str] = None,
        reserva_recorrente_id: Optional[str] = None,
        acao: str = None,
        dados_anteriores: str = None,
        dados_novos: str = None,
        usuario_id: str = None,
        ip_address: str = None,
        motivo: str = None,
    ) -> AuditoriaReserva:
        """
        Cria um novo registro de auditoria.
        """
        # Converte as strings JSON para objetos Python
        dados_anteriores_obj = (
            json.loads(dados_anteriores) if dados_anteriores else None
        )
        dados_novos_obj = json.loads(dados_novos) if dados_novos else None

        auditoria = AuditoriaReserva(
            reserva_id=reserva_id,
            reserva_recorrente_id=reserva_recorrente_id,
            acao=acao,
            dados_anteriores=dados_anteriores_obj,
            dados_novos=dados_novos_obj,
            usuario_id=usuario_id,
            ip_address=ip_address,
            motivo=motivo,
            criado_em=DateTimeUtils.now(),
        )
        print(f"Auditoria: {auditoria}")
        self.session.add(auditoria)
        self.session.commit()
        self.session.refresh(auditoria)
        return auditoria

    def listar_por_reserva(self, reserva_id: str) -> List[AuditoriaReserva]:
        """
        Lista todas as auditorias de uma reserva específica.
        """
        return (
            self.session.query(AuditoriaReserva)
            .filter(AuditoriaReserva.reserva_id == reserva_id)
            .order_by(AuditoriaReserva.criado_em.desc())
            .all()
        )

    def listar_por_reserva_recorrente(
        self, reserva_recorrente_id: str
    ) -> List[AuditoriaReserva]:
        """
        Lista todas as auditorias de uma reserva recorrente específica.
        """
        return (
            self.session.query(AuditoriaReserva)
            .filter(AuditoriaReserva.reserva_recorrente_id == reserva_recorrente_id)
            .order_by(AuditoriaReserva.criado_em.desc())
            .all()
        )

    def listar_por_usuario(self, usuario_id: str) -> List[AuditoriaReserva]:
        """
        Lista todas as auditorias realizadas por um usuário específico.
        """
        return (
            self.session.query(AuditoriaReserva)
            .filter(AuditoriaReserva.usuario_id == usuario_id)
            .order_by(AuditoriaReserva.criado_em.desc())
            .all()
        )

    def listar_por_periodo(
        self, data_inicio: DateTimeUtils, data_fim: DateTimeUtils
    ) -> List[AuditoriaReserva]:
        """
        Lista todas as auditorias em um período específico.
        """
        return (
            self.session.query(AuditoriaReserva)
            .filter(AuditoriaReserva.criado_em.between(data_inicio, data_fim))
            .order_by(AuditoriaReserva.criado_em.desc())
            .all()
        )
