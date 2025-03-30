from typing import Optional, List
from datetime import date, time
from sqlalchemy.orm import Session

from app.model.reserva_recorrente_model import ReservaRecorrente
from app.repository.base_repository import BaseRepository
from app.schema.reserva_schema import (
    ReservaRecorrenteFiltros,
    ReservasRecorrentesPaginadas,
)
from app.core.commons.responses import InformacoesPaginacao


class ReservaRecorrenteRepository(BaseRepository):
    """Repositório responsável pelo acesso aos dados de reservas recorrentes"""

    def __init__(self, session: Session):
        super().__init__(session, ReservaRecorrente)
        self.session = session

    def get_by_query(
        self, filtros: ReservaRecorrenteFiltros
    ) -> ReservasRecorrentesPaginadas:
        """Busca reservas recorrentes com filtros e paginação"""
        query = self.session.query(ReservaRecorrente)

        if filtros.sala_id:
            query = query.filter(ReservaRecorrente.sala_id == filtros.sala_id)
        if filtros.usuario_id:
            query = query.filter(ReservaRecorrente.usuario_id == filtros.usuario_id)
        if filtros.frequencia:
            query = query.filter(ReservaRecorrente.frequencia == filtros.frequencia)
        if filtros.data_inicio:
            query = query.filter(ReservaRecorrente.data_inicio >= filtros.data_inicio)
        if filtros.data_fim:
            query = query.filter(ReservaRecorrente.data_fim <= filtros.data_fim)

        offset = (filtros.pagina - 1) * filtros.tamanho
        total = query.count()
        items = query.offset(offset).limit(filtros.tamanho).all()
        total_pages = (total + filtros.tamanho - 1) // filtros.tamanho

        return ReservasRecorrentesPaginadas(
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

    def check_conflict(
        self,
        sala_id: str,
        data_inicio: date,
        data_fim: date,
        hora_inicio: time,
        hora_fim: time,
        dia_da_semana: List[int],
        exclude_id: Optional[str] = None,
    ) -> bool:
        """Verifica se existe conflito de horário para a sala recorrente"""
        query = self.session.query(ReservaRecorrente).filter(
            ReservaRecorrente.sala_id == sala_id,
            ReservaRecorrente.data_inicio <= data_fim,
            ReservaRecorrente.data_fim >= data_inicio,
            ReservaRecorrente.dia_da_semana.op('&&')(dia_da_semana),
            ReservaRecorrente.hora_inicio <= hora_fim,
            ReservaRecorrente.hora_fim >= hora_inicio,
        )

        if exclude_id:
            query = query.filter(ReservaRecorrente.id != exclude_id)

        return query.count() > 0

    def get_by_period(
        self, sala_id: str, data_inicio: date, data_fim: date
    ) -> List[ReservaRecorrente]:
        """Busca reservas recorrentes de uma sala em um período"""
        return (
            self.session.query(ReservaRecorrente)
            .filter(
                ReservaRecorrente.sala_id == sala_id,
                ReservaRecorrente.data_inicio <= data_fim,
                ReservaRecorrente.data_fim >= data_inicio,
            )
            .all()
        )
