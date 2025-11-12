from pydantic import BaseModel
from datetime import date
from typing import Optional

class CuotaBase(BaseModel):
    alumno_id: int
    periodo: str
    fecha_vencimiento: date
    monto_base: float
    ajuste_anterior: Optional[float] = 0
    monto_a_pagar: float
    monto_pagado: Optional[float] = 0
    saldo_pendiente: Optional[float] = 0
    estado: Optional[str] = "pendiente"

class CuotaOut(CuotaBase):
    id: int

    class Config:
        from_attributes = True