from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class NotificacionPagoBase(BaseModel):
    alumno_id: int
    cuota_id: int
    tipo: str
    destinatario: str
    mensaje: str


class NotificacionPagoCreate(NotificacionPagoBase):
    """Schema para crear una nueva notificación manual o automática."""
    pass


class NotificacionPagoOut(NotificacionPagoBase):
    id: int
    fecha_envio: datetime
    # 🔹 Campos adicionales para mostrar más info en el frontend
    alumno_nombre: Optional[str] = None
    periodo: Optional[str] = None

    class Config:
        from_attributes = True