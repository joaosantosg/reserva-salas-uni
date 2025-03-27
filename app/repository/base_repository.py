from typing import Any, Type, TypeVar
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.core.commons.exceptions import (
    DuplicatedException,
    NotFoundException,
    BusinessException,
)
from app.core.commons.responses import InformacoesPaginacao
from app.model.base_model import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseRepository:
    def __init__(self, session: Session, model: Type[T]) -> None:
        self.session = session
        self.model = model

    def get_by_id(self, id: Any, eager: bool = False) -> T:
        """Busca um registro por ID"""
        query = self.session.query(self.model)
        if eager and hasattr(self.model, "eagers"):
            for eager_field in getattr(self.model, "eagers"):
                query = query.options(joinedload(getattr(self.model, eager_field)))

        result = query.filter(self.model.id == id).first()
        if not result:
            raise NotFoundException(f"Registro com ID {id} não encontrado")
        return result

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
            # Verifica se é um erro de chave duplicada
            if "duplicate key" in str(e).lower():
                raise DuplicatedException(f"Registro com ID {model.id} já existe")
            # Para outros erros de integridade
            raise BusinessException(f"Erro ao salvar registro: {str(e)}")
        except Exception as e:
            self.session.rollback()
            raise BusinessException(f"Erro ao salvar registro: {str(e)}")

    def delete(self, id: Any) -> None:
        """Remove um registro"""
        instance = self.get_by_id(id)
        self.session.delete(instance)
        self.session.commit()

    def get_all(self, page: int = 1, size: int = 10, eager: bool = False) -> dict:
        """Busca todos os registros com paginação"""
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

    def update(self, id: Any, data: dict) -> T:
        """Atualiza um registro existente"""
        instance = self.get_by_id(id)
        for key, value in data.items():
            setattr(instance, key, value)
        self.session.commit()
        return instance

    def close_scoped_session(self):
        self.session.close()
