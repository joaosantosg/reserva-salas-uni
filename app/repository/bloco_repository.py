from typing import Optional
from sqlalchemy.orm import Session

from app.model.bloco_model import Bloco
from app.repository.base_repository import BaseRepository
from app.schema.bloco_schema import BlocoFiltros, BlocosPaginados
from app.core.commons.responses import InformacoesPaginacao

class BlocoRepository(BaseRepository):
    """Repositório responsável pelo acesso aos dados de blocos"""
    
    def __init__(self, session: Session):
        super().__init__(session, Bloco)
        self.session = session

    def get_by_query(self, query: BlocoFiltros) -> BlocosPaginados:
        """Busca blocos com filtros e paginação"""
        query_obj = self.session.query(Bloco)
        
        if query.nome:
            query_obj = query_obj.filter(Bloco.nome.ilike(f"%{query.nome}%"))
        if query.identificacao:
            query_obj = query_obj.filter(Bloco.identificacao.ilike(f"%{query.identificacao}%"))

        offset = (query.pagina - 1) * query.tamanho
        total = query_obj.count()
        items = query_obj.offset(offset).limit(query.tamanho).all()
        total_pages = (total + query.tamanho - 1) // query.tamanho
        
        return BlocosPaginados(
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

    def get_by_identificacao(self, identificacao: str) -> Optional[Bloco]:
        """Busca bloco por identificação"""
        return self.session.query(self.model).filter(self.model.identificacao == identificacao).first() 