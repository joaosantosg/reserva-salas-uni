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
        self, query: ReservaRecorrenteFiltros
    ) -> ReservasRecorrentesPaginadas:
        """Busca reservas recorrentes com filtros e paginação"""
        query = self.session.query(ReservaRecorrente)

        if query.sala_id:
            query = query.filter(ReservaRecorrente.sala_id == query.sala_id)
        if query.coordenador_id:
            query = query.filter(ReservaRecorrente.usuario_id == query.coordenador_id)
        if query.frequencia:
            query = query.filter(ReservaRecorrente.frequencia == query.frequencia)
        if query.data_inicio:
            query = query.filter(ReservaRecorrente.data_inicio >= query.data_inicio)
        if query.data_fim:
            query = query.filter(ReservaRecorrente.data_fim <= query.data_fim)

        offset = (query.pagina - 1) * query.tamanho
        total = query.count()
        items = query.offset(offset).limit(query.tamanho).all()
        total_pages = (total + query.tamanho - 1) // query.tamanho

        return ReservasRecorrentesPaginadas(
            items=items,
            paginacao=InformacoesPaginacao(
                total=total,
                pagina=query.pagina,
                tamanho=query.tamanho,
                total_paginas=total_pages,
                proxima=query.pagina < total_pages,
                anterior=query.pagina > 1,
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
            ReservaRecorrente.dia_da_semana.overlap(dia_da_semana),
        )

        if exclude_id:
            query = query.filter(ReservaRecorrente.id != exclude_id)

        return query.first() is not None

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
