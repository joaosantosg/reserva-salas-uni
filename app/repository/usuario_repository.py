from typing import Optional
from sqlalchemy.orm import Session

from app.model.usuario_model import Usuario
from app.repository.base_repository import BaseRepository
from app.schema.usuario_schema import UsuarioFiltros, UsuariosPaginados
from app.core.commons.responses import InformacoesPaginacao


class UsuarioRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session, Usuario)
        self.session = session

    def get_by_query(self, filtros: UsuarioFiltros) -> UsuariosPaginados:
        query = self.session.query(Usuario)
        if filtros.nome is not None:
            query = query.filter(Usuario.nome.ilike(f"%{filtros.nome}%"))
        if filtros.email:
            query = query.filter(Usuario.email.ilike(f"%{filtros.email}%"))
        if filtros.matricula:
            query = query.filter(Usuario.matricula.ilike(f"%{filtros.matricula}%"))
        if filtros.curso:
            query = query.filter(Usuario.curso.ilike(f"%{filtros.curso}%"))
        if filtros.ativo:
            query = query.filter(Usuario.ativo == filtros.ativo)
        if filtros.super_user:
            query = query.filter(Usuario.super_user == filtros.super_user)

        offset = (filtros.pagina - 1) * filtros.tamanho
        total = query.count()
        items = query.offset(offset).limit(filtros.tamanho).all()
        total_pages = (total + filtros.tamanho - 1) // filtros.tamanho
        return UsuariosPaginados(
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

    def get_by_email(self, email: str) -> Optional[Usuario]:
        """Busca usuário por email"""
        return self.session.query(Usuario).filter(Usuario.email == email).first()

    def get_by_matricula(self, matricula: str) -> Optional[Usuario]:
        """Busca usuário por matrícula"""
        return (
            self.session.query(Usuario).filter(Usuario.matricula == matricula).first()
        )
