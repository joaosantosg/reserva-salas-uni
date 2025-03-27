from uuid import UUID
from app.repository.bloco_repository import BlocoRepository
from app.services.base_service import BaseService
from app.core.commons.exceptions import NotFoundException, BusinessException
from app.model.bloco_model import Bloco
from app.schema.bloco_schema import (
    BlocoCreate,
    BlocoUpdate,
    BlocoFiltros,
    BlocosPaginados,
)


class BlocoService(BaseService):
    """Serviço responsável pela gestão de blocos"""

    def __init__(self, bloco_repository: BlocoRepository):
        super().__init__(bloco_repository)
        self.bloco_repository = bloco_repository

    def get_by_id(self, bloco_id: UUID) -> Bloco:
        """Busca um bloco pelo ID"""
        bloco = self.bloco_repository.get_by_id(bloco_id)
        if not bloco:
            raise NotFoundException(f"Bloco com ID {bloco_id} não encontrado")
        return bloco

    def create(self, bloco_data: BlocoCreate) -> Bloco:
        """Cria um novo bloco"""
        # Verificar se já existe um bloco com a mesma identificação
        if self.bloco_repository.get_by_identificacao(bloco_data.identificacao):
            raise BusinessException(
                f"Já existe um bloco com a identificação {bloco_data.identificacao}"
            )

        return self.bloco_repository.save(Bloco(**bloco_data.model_dump()))

    def update(self, bloco_id: UUID, bloco_data: BlocoUpdate) -> Bloco:
        """Atualiza um bloco existente"""
        bloco = self.get_by_id(bloco_id)

        # Verificar se a identificação já está em uso
        if bloco_data.identificacao and bloco_data.identificacao != bloco.identificacao:
            if self.bloco_repository.get_by_identificacao(bloco_data.identificacao):
                raise BusinessException(
                    f"Já existe um bloco com a identificação {bloco_data.identificacao}"
                )

        return self.bloco_repository.update(bloco_id, bloco_data)

    def delete(self, bloco_id: UUID) -> Bloco:
        """Remove um bloco"""
        bloco = self.get_by_id(bloco_id)

        # TODO: Verificar se o bloco possui salas vinculadas
        # TODO: Se possuir, lançar uma exceção
        # TODO: Se não possuir, deletar o bloco

        self.bloco_repository.delete(bloco_id)
        return bloco

    def get_by_query(self, filtros: BlocoFiltros) -> BlocosPaginados:
        """Busca blocos com filtros e paginação"""
        return self.bloco_repository.get_by_query(filtros)
