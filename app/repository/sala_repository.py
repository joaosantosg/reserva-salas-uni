from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from sqlalchemy.orm import joinedload
from uuid import UUID

from app.model.sala_model import Sala
from app.repository.base_repository import BaseRepository
from app.schema.sala_schema import SalaFiltros, SalasPaginadas
from app.core.commons.responses import InformacoesPaginacao


class SalaRepository(BaseRepository):
    """Repositório responsável pelo acesso aos dados de salas"""

    def __init__(self, session: Session):
        super().__init__(session, Sala)
        self.session = session

    def get_by_query(self, filtros: SalaFiltros) -> SalasPaginadas:
        """Busca salas com filtros e paginação"""
        query = self.session.query(Sala)

        if filtros.bloco_id:
            query = query.filter(Sala.bloco_id == filtros.bloco_id)
        if filtros.capacidade_maxima:
            query = query.filter(Sala.capacidade_maxima >= filtros.capacidade_maxima)
        if filtros.uso_restrito:
            query = query.filter(Sala.uso_restrito == filtros.uso_restrito)
        if filtros.curso_restrito:
            query = query.filter(Sala.curso_restrito == filtros.curso_restrito)

        query = query.options(joinedload(Sala.bloco))
        query = query.order_by(Sala.identificacao_sala.asc())
        offset = (filtros.pagina - 1) * filtros.tamanho
        total = query.count()
        items = query.offset(offset).limit(filtros.tamanho).all()
        total_pages = (total + filtros.tamanho - 1) // filtros.tamanho

        return SalasPaginadas(
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

    def check_identificacao_sala_exists(
        self, bloco_id: str, identificacao_sala: str, exclude_id: Optional[str] = None
    ) -> bool:
        """Verifica se já existe uma sala com a mesma identificação no bloco"""
        query = self.session.query(Sala).filter(
            Sala.bloco_id == bloco_id, Sala.identificacao_sala == identificacao_sala
        )

        if exclude_id:
            query = query.filter(Sala.id != exclude_id)

        return query.first() is not None

    def get_by_bloco(self, bloco_id: UUID) -> List[Sala]:
        """Busca todas as salas de um bloco"""
        return (
            self.session.query(Sala)
            .filter(and_(Sala.bloco_id == bloco_id, Sala.excluido_em.is_(None)))
            .all()
        )

    def count_all(self) -> int:
        """
        Retorna o total de salas ativas.

        Returns:
            Total de salas ativas
        """
        return (
            self.session.query(Sala)
            .filter(Sala.excluido_em.is_(None))
            .count()
        )

    def get_by_id(self, sala_id: UUID) -> Sala:
        """
        Busca uma sala pelo ID.

        Args:
            sala_id: ID da sala

        Returns:
            Sala encontrada ou None se não existir
        """
        return (
            self.session.query(Sala)
            .filter(and_(Sala.id == sala_id, Sala.excluido_em.is_(None)))
            .first()
        )
