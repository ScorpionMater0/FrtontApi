from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# 📥 Entrada de pago normal

class PagoBase(BaseModel):
    alumno_id: int
    cuota_id: Optional[int]
    monto_pagado: float
    metodo: str
    comprobante: Optional[str] = None


# 📤 Salida de pago

class PagoOut(BaseModel):
    id: int
    alumno_id: int
    monto_pagado: float
    fecha_pago: datetime
    metodo: str
    comprobante: Optional[str]
    cuota_id: Optional[int]
    periodo: Optional[str]

    class Config:
        from_attributes = True




# 📚 MODELO PAGOS ELIMINADOS (Historial)

# 📥 Entrada (motivo opcional)

class PagoEliminadoIn(BaseModel):
    motivo: Optional[str] = "No especificado"


# 📤 Salida básica

class PagoEliminadoOut(BaseModel):
    id: int
    pago_id_original: int
    alumno_id: int
    cuota_id: Optional[int]
    monto_pagado: float
    metodo: str
    comprobante: Optional[str]
    fecha_pago: datetime
    fecha_eliminacion: datetime
    eliminado_por: int
    motivo: Optional[str]

    class Config:
        from_attributes = True


# 📤 Versión extendida (para reportes o panel admin)

class PagoEliminadoDetailOut(PagoEliminadoOut):
    alumno_nombre: Optional[str]
    eliminado_por_nombre: Optional[str]
