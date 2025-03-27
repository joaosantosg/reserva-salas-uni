from uuid import UUID
from app.repository.usuario_repository import UsuarioRepository
from app.services.base_service import BaseService
from app.core.commons.exceptions import NotFoundException, BusinessException
from app.model.usuario_model import Usuario
from app.schema.usuario_schema import (
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioFiltros,
    UsuariosPaginados,
)


class UsuarioService(BaseService):
    def __init__(self, usuario_repository: UsuarioRepository):
        super().__init__(usuario_repository)
        self.usuario_repository = usuario_repository

    def get_by_id(self, usuario_id: UUID) -> Usuario:
        usuario = self.usuario_repository.get_by_id(usuario_id)
        if not usuario:
            raise NotFoundException(f"Usuário com ID {usuario_id} não encontrado")
        return usuario

    def create(self, usuario_data: UsuarioCreate) -> Usuario:
        # TODO: Melhorar perfomance para evitar buscar por email e matricula duas vezes
        if self.usuario_repository.get_by_email(usuario_data.email):
            raise BusinessException("Email já cadastrado")
        if self.usuario_repository.get_by_matricula(usuario_data.matricula):
            raise BusinessException("Matrícula já cadastrada")

        user_model = Usuario(**usuario_data.model_dump())
        user_model.set_senha(usuario_data.senha)
        return self.usuario_repository.save(user_model)

    def update(self, usuario_id: UUID, usuario_data: UsuarioUpdate) -> Usuario:
        usuario = self.get_by_id(usuario_id)
        if usuario_data.nome:
            usuario.nome = usuario_data.nome
        if usuario_data.email:
            usuario.email = usuario_data.email
        if usuario_data.matricula:
            usuario.matricula = usuario_data.matricula
        if usuario_data.curso:
            usuario.curso = usuario_data.curso
        if usuario_data.ativo:
            usuario.ativo = usuario_data.ativo
        if usuario_data.senha:
            usuario.set_senha(usuario_data.senha)
        return self.usuario_repository.save(usuario)

    def delete(self, usuario_id: UUID) -> Usuario:
        usuario = self.get_by_id(usuario_id)
        if usuario is None:
            raise NotFoundException(f"Usuário com ID {usuario_id} não encontrado")
        self.usuario_repository.delete(usuario_id)
        return usuario

    def get_by_query(self, filtros: UsuarioFiltros) -> UsuariosPaginados:
        return self.usuario_repository.get_by_query(filtros)
