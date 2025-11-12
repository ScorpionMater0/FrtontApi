from pydantic import BaseModel
from datetime import date
from typing import Optional

class TarifaBase(BaseModel):
    monto_mensual: float
    vigente_desde: date
    vigente_hasta: Optional[date] = None

class TarifaCreate(TarifaBase):
    creado_por: Optional[int] = None

class TarifaOut(TarifaBase):
    id: int

    class Config:
        from_attributes = True