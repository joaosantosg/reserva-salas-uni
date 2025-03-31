from typing import Any, Type, TypeVar, Optional
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, OperationalError
from sqlalchemy.orm import Session, joinedload
import logging

from app.core.commons.exceptions import (
    DuplicatedException,
    NotFoundException,
    BusinessException,
)
from app.core.commons.responses import InformacoesPaginacao
from app.model.base_model import BaseModel

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class BaseRepository:
    def __init__(self, session: Session, model: Type[T]) -> None:
        self.session = session
        self.model = model

    def get_by_id(self, id: Any, eager: bool = False) -> T:
        """Busca um registro por ID"""
        try:
            query = self.session.query(self.model)
            if eager and hasattr(self.model, "eagers"):
                for eager_field in getattr(self.model, "eagers"):
                    query = query.options(joinedload(getattr(self.model, eager_field)))

            result = query.filter(self.model.id == id).first()
            if not result:
                raise NotFoundException(f"Registro com ID {id} não encontrado")
            return result
        except SQLAlchemyError as e:
            logger.error(f"Erro ao buscar registro por ID: {str(e)}")
            raise BusinessException(f"Erro ao buscar registro: {str(e)}")

    def save(self, model: T) -> T:
        """
        Salva ou atualiza um registro.
        Se o registro já existe (tem ID), atualiza.
        Se não existe, cria um novo.
        """
        try:
            # Verifica se o registro já existe
            if model.id and self.session.get(self.model, model.id):
                self.session.merge(model)
            else:
                self.session.add(model)

            self.session.commit()
            self.session.refresh(model)
            return model
        except IntegrityError as e:
            self.session.rollback()
            logger.error(f"Erro de integridade ao salvar registro: {str(e)}")
            if "duplicate key" in str(e).lower():
                raise DuplicatedException(f"Registro com ID {model.id} já existe")
            raise BusinessException(f"Erro de integridade ao salvar registro: {str(e)}")
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Erro SQLAlchemy ao salvar registro: {str(e)}")
            raise BusinessException(f"Erro ao salvar registro: {str(e)}")
        except Exception as e:
            self.session.rollback()
            logger.error(f"Erro inesperado ao salvar registro: {str(e)}")
            raise BusinessException(f"Erro ao salvar registro: {str(e)}")
        
    def create(self, model: T) -> T:
        """Cria um novo registro"""
        try:
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return model
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Erro ao criar registro: {str(e)}")
            raise BusinessException(f"Erro ao criar registro: {str(e)}")

    def delete(self, id: Any) -> None:
        """Remove um registro"""
        try:
            instance = self.get_by_id(id)
            self.session.delete(instance)
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Erro ao deletar registro: {str(e)}")
            raise BusinessException(f"Erro ao deletar registro: {str(e)}")

    def get_all(self, page: int = 1, size: int = 10, eager: bool = False) -> dict:
        """Busca todos os registros com paginação"""
        try:
            query = self.session.query(self.model)

            if eager and hasattr(self.model, "eagers"):
                for eager_field in getattr(self.model, "eagers"):
                    query = query.options(joinedload(getattr(self.model, eager_field)))

            query = query.order_by(self.model.id.asc())

            total = query.count()
            if size == "all":
                items = query.all()
            else:
                items = query.offset((page - 1) * size).limit(size).all()

            total_pages = (total + size - 1) // size if size != "all" else 1
            paginacao = InformacoesPaginacao(
                total=total,
                pagina=page,
                tamanho=size,
                total_paginas=total_pages,
                proxima=page < total_pages,
                anterior=page > 1,
            )

            return {"items": items, "paginacao": paginacao}
        except SQLAlchemyError as e:
            logger.error(f"Erro ao buscar registros: {str(e)}")
            raise BusinessException(f"Erro ao buscar registros: {str(e)}")

    def update(self, id: Any, data: dict) -> T:
        """Atualiza um registro existente"""
        try:
            instance = self.get_by_id(id)
            for key, value in data.items():
                setattr(instance, key, value)
            self.session.commit()
            return instance
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Erro ao atualizar registro: {str(e)}")
            raise BusinessException(f"Erro ao atualizar registro: {str(e)}")

    def close_scoped_session(self):
        """Fecha a sessão do repositório"""
        try:
            self.session.close()
        except SQLAlchemyError as e:
            logger.error(f"Erro ao fechar sessão: {str(e)}")
            raise BusinessException(f"Erro ao fechar sessão: {str(e)}")
