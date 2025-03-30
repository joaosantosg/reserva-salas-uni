from typing import List
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from sqlalchemy.orm import joinedload
from uuid import UUID

from app.model.reserva_model import Reserva
from app.repository.base_repository import BaseRepository
from app.schema.reserva_schema import ReservaFiltros, ReservasPaginadas
from app.core.commons.responses import InformacoesPaginacao
from app.util.datetime_utils import DateTimeUtils


class ReservaRepository(BaseRepository):
    """Repositório responsável pelo acesso aos dados de reservas regulares"""

    def __init__(self, session: Session):
        super().__init__(session, Reserva)
        self.session = session

    def get_by_query(self, filtros: ReservaFiltros) -> ReservasPaginadas:
        """Busca reservas com filtros e paginação"""
        query = self.session.query(Reserva)

        if filtros.sala_id:
            query = query.filter(Reserva.sala_id == filtros.sala_id)
        if filtros.usuario_id:
            query = query.filter(Reserva.usuario_id == filtros.usuario_id)
        if filtros.data_inicio:
            query = query.filter(Reserva.inicio >= filtros.data_inicio)
        if filtros.data_fim:
            query = query.filter(Reserva.fim <= filtros.data_fim)

        query = query.options(joinedload(Reserva.sala), joinedload(Reserva.usuario))
        query = query.order_by(Reserva.inicio.asc())
        offset = (filtros.pagina - 1) * filtros.tamanho
        total = query.count()
        items = query.offset(offset).limit(filtros.tamanho).all()
        total_pages = (total + filtros.tamanho - 1) // filtros.tamanho

        return ReservasPaginadas(
            items=items,
            paginacao=InformacoesPaginacao(
                total=total,
                pagina=filtros.pagina,
                tamanho=filtros.tamanho,
                total_paginas=total_pages,
                proxima=filtros.pagina < total_pages,
                anterior=filtros.pagina > 1,
            ),
        )

    def get_by_period(
        self, sala_id: str, inicio: datetime, fim: datetime
    ) -> List[Reserva]:
        """Busca reservas de uma sala em um período"""
        return (
            self.session.query(Reserva)
            .filter(
                Reserva.sala_id == sala_id, Reserva.inicio >= inicio, Reserva.fim <= fim
            )
            .all()
        )

    def soft_delete_reservas_recorrentes(
        self, reserva_recorrente_id: UUID, usuario_id: UUID
    ) -> None:
        """Realiza soft delete de todas as reservas de uma reserva recorrente"""
        self.session.query(Reserva).filter(
            Reserva.reserva_recorrente_id == reserva_recorrente_id,
            Reserva.excluido_em.is_(None),
        ).update(
            {
                Reserva.excluido_em: DateTimeUtils.now(),
                Reserva.excluido_por_id: usuario_id,
            }
        )
        self.session.commit()

    def get_by_sala_and_date(self, sala_id: UUID, data: date) -> List[Reserva]:
        """
        Busca todas as reservas de uma sala em uma data específica.

        Args:
            sala_id: ID da sala
            data: Data para buscar as reservas

        Returns:
            Lista de reservas da sala na data especificada
        """
        return (
            self.session.query(Reserva)
            .filter(
                and_(
                    Reserva.sala_id == sala_id,
                    func.date(Reserva.inicio) == data,
                    Reserva.excluido_em.is_(None),
                )
            )
            .all()
        )
