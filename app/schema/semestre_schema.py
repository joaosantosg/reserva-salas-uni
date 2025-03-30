from datetime import date
from pydantic import BaseModel, field_validator, model_validator
from app.core.commons.exceptions import ValidationException
import re



class SemestreBase(BaseModel):
    """Schema base para semestre"""

    identificador: str
    data_inicio: date
    data_fim: date
    ativo: bool = True

    @field_validator("identificador")
    def validar_identificador(cls, v):
        if len(v) != 6:
            raise ValidationException("O identificador deve ter exatamente 6 caracteres")
        ## Validar formato do identificador YYYY.X
        if not re.match(r'^\d{4}\.\d$', v):
            raise ValidationException("O identificador deve estar no formato YYYY.X")
        return v
    
    @model_validator(mode='after')
    def validar_datas(self) -> 'SemestreBase':
        if self.data_inicio > self.data_fim:
            raise ValidationException("A data de início não pode ser maior que a data de fim")
        return self
    
    


    class Config:
        from_attributes = True

class SemestreCreate(SemestreBase):
    """Schema para criação de semestre"""

    pass

class SemestreUpdate(SemestreBase):
    """Schema para atualização de semestre"""

    pass

class SemestreResponse(SemestreBase):
    """Schema para resposta de semestre"""
    pass 