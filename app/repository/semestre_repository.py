from typing import List, Optional
from sqlalchemy.orm import Session
from app.repository.base_repository import BaseRepository
from app.model.semestre_model import Semestre

class SemestreRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session, Semestre)

    def get_all(self) -> List[Semestre]:
        return self.session.query(Semestre).all()

    def get_by_identificador(self, identificador: str) -> Optional[Semestre]:
        return self.session.query(Semestre).filter(Semestre.identificador == identificador).first()
    