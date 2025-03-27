from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.model.sala_model import Sala
from app.repository.base_repository import BaseRepository
from app.schema.sala_schema import SalaFiltros, SalasPaginadas
from app.core.commons.responses import InformacoesPaginacao

class SalaRepository(BaseRepository):
    """Repositório responsável pelo acesso aos dados de salas"""
    
    def __init__(self, session: Session):
        super().__init__(session, Sala)
        self.session = session

    def get_by_query(self, query: SalaFiltros) -> SalasPaginadas:
        """Busca salas com filtros e paginação"""
        query_obj = self.session.query(Sala)
        
        if query.bloco_id:
            query_obj = query_obj.filter(Sala.bloco_id == query.bloco_id)
        if query.identificacao_sala:
            query_obj = query_obj.filter(Sala.identificacao_sala.ilike(f"%{query.identificacao_sala}%"))
        if query.capacidade_minima:
            query_obj = query_obj.filter(Sala.capacidade_maxima >= query.capacidade_minima)
        if query.uso_restrito is not None:
            query_obj = query_obj.filter(Sala.uso_restrito == query.uso_restrito)
        if query.curso_restrito:
            query_obj = query_obj.filter(Sala.curso_restrito == query.curso_restrito)

        offset = (query.pagina - 1) * query.tamanho
        total = query_obj.count()
        items = query_obj.offset(offset).limit(query.tamanho).all()
        total_pages = (total + query.tamanho - 1) // query.tamanho
        
        return SalasPaginadas(
            items=items,
            paginacao=InformacoesPaginacao(
                total=total,
                pagina=query.pagina,
                tamanho=query.tamanho,
                total_paginas=total_pages,
                proxima=query.pagina < total_pages,
                anterior=query.pagina > 1
            )
        )

    def check_identificacao_sala_exists(self, bloco_id: str, identificacao_sala: str, exclude_id: Optional[str] = None) -> bool:
        """Verifica se já existe uma sala com a mesma identificação no bloco"""
        query = self.session.query(Sala).filter(
            Sala.bloco_id == bloco_id,
            Sala.identificacao_sala == identificacao_sala
        )
        
        if exclude_id:
            query = query.filter(Sala.id != exclude_id)
            
        return query.first() is not None

    def get_by_bloco(self, bloco_id: str) -> List[Sala]:
        """Busca todas as salas de um bloco"""
        return self.session.query(Sala).filter(Sala.bloco_id == bloco_id).all() 