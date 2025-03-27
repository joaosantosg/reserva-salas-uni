from uuid import UUID
from app.repository.sala_repository import SalaRepository
from app.repository.bloco_repository import BlocoRepository
from app.services.base_service import BaseService
from app.core.commons.exceptions import NotFoundException, BusinessException
from app.model.sala_model import Sala
from app.schema.sala_schema import SalaCreate, SalaUpdate, SalaFiltros, SalasPaginadas


class SalaService(BaseService):
    """Serviço responsável pela gestão de salas"""

    def __init__(
        self, sala_repository: SalaRepository, bloco_repository: BlocoRepository
    ):
        super().__init__(sala_repository)
        self.sala_repository = sala_repository
        self.bloco_repository = bloco_repository

    def get_by_id(self, sala_id: UUID) -> Sala:
        """Busca uma sala pelo ID"""
        sala = self.sala_repository.get_by_id(sala_id)
        if not sala:
            raise NotFoundException(f"Sala com ID {sala_id} não encontrada")
        return sala

    def create(self, sala_data: SalaCreate) -> Sala:
        """Cria uma nova sala"""
        # Verificar se o bloco existe
        if not self.bloco_repository.get_by_id(sala_data.bloco_id):
            raise NotFoundException(f"Bloco com ID {sala_data.bloco_id} não encontrado")

        # Verificar se já existe uma sala com a mesma identificação no bloco
        if self.sala_repository.check_identificacao_sala_exists(
            sala_data.bloco_id, sala_data.identificacao_sala
        ):
            raise BusinessException(
                f"Já existe uma sala com a identificação {sala_data.identificacao_sala} neste bloco"
            )

        # Validação da capacidade máxima
        if sala_data.capacidade_maxima <= 0:
            raise BusinessException(
                "A capacidade máxima da sala deve ser maior que zero"
            )

        # Validação de curso restrito
        if sala_data.uso_restrito and not sala_data.curso_restrito:
            raise BusinessException(
                "É necessário informar o curso restrito para salas de uso restrito"
            )

        return self.sala_repository.save(Sala(**sala_data.model_dump()))

    def update(self, sala_id: UUID, sala_data: SalaUpdate) -> Sala:
        """Atualiza uma sala existente"""
        sala_in_db = self.get_by_id(sala_id)

        # Verificar se já existe uma sala com a mesma identificação no bloco
        if (
            sala_data.identificacao_sala
            and sala_data.identificacao_sala != sala_in_db.identificacao_sala
        ):
            if self.sala_repository.check_identificacao_sala_exists(
                sala_in_db.bloco_id, sala_data.identificacao_sala, sala_id
            ):
                raise BusinessException(
                    f"Já existe uma sala com a identificação {sala_data.identificacao_sala} neste bloco"
                )

        # Validação da capacidade máxima
        if sala_data.capacidade_maxima is not None and sala_data.capacidade_maxima <= 0:
            raise BusinessException(
                "A capacidade máxima da sala deve ser maior que zero"
            )

        # Validação de curso restrito
        uso_restrito = (
            sala_data.uso_restrito
            if sala_data.uso_restrito is not None
            else sala_in_db.uso_restrito
        )
        curso_restrito = (
            sala_data.curso_restrito
            if sala_data.curso_restrito is not None
            else sala_in_db.curso_restrito
        )

        if uso_restrito and not curso_restrito:
            raise BusinessException(
                "É necessário informar o curso restrito para salas de uso restrito"
            )

        if sala_data.recursos:
            sala_in_db.recursos = sala_data.recursos
        if sala_data.capacidade_maxima:
            sala_in_db.capacidade_maxima = sala_data.capacidade_maxima
        if sala_data.uso_restrito:
            sala_in_db.uso_restrito = sala_data.uso_restrito
        if sala_data.curso_restrito:
            sala_in_db.curso_restrito = sala_data.curso_restrito
        if sala_data.identificacao_sala:
            sala_in_db.identificacao_sala = sala_data.identificacao_sala

            return self.sala_repository.save(sala_in_db)

    def delete(self, sala_id: UUID) -> Sala:
        """Remove uma sala"""
        sala = self.get_by_id(sala_id)

        # Aqui poderia verificar se existem reservas para esta sala
        # Mas isso seria feito em outro momento ou por constraint no banco

        self.sala_repository.delete(sala_id)
        return sala

    def get_by_query(self, filtros: SalaFiltros) -> SalasPaginadas:
        """Busca salas com filtros e paginação"""
        return self.sala_repository.get_by_query(filtros)

    def get_by_bloco(self, bloco_id: UUID) -> list[Sala]:
        """Busca todas as salas de um bloco"""
        # Verificar se o bloco existe
        if not self.bloco_repository.get_by_id(bloco_id):
            raise NotFoundException(f"Bloco com ID {bloco_id} não encontrado")

        return self.sala_repository.get_by_bloco(bloco_id)
