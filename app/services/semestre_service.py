from typing import List, Optional
from app.services.base_service import BaseService
from app.repository.semestre_repository import SemestreRepository
from app.model.semestre_model import Semestre
from app.schema.semestre_schema import SemestreCreate
from app.core.commons.exceptions import ValidationException
from uuid import UUID

class SemestreService(BaseService):
    def __init__(self, semestre_repository: SemestreRepository):
        super().__init__(semestre_repository)
        self.semestre_repository = semestre_repository

    def create(self, semestre: SemestreCreate) -> Semestre:

        if self.semestre_repository.get_by_identificador(semestre.identificador):
            raise ValidationException("Já existe um semestre com o identificador informado")

        semestre = Semestre(
            identificador=semestre.identificador,
            data_inicio=semestre.data_inicio,
            data_fim=semestre.data_fim,
            ativo=semestre.ativo,
        )
        return self.semestre_repository.create(semestre)

    def get_all(self) -> List[Semestre]:
        return self.semestre_repository.get_all()

    def get_by_id(self, id: UUID) -> Optional[Semestre]:
        return self.semestre_repository.get_by_id(id)
    
    def get_by_identificador(self, identificador: str) -> Optional[Semestre]:
        return self.semestre_repository.get_by_identificador(identificador)
