from config.db import Base
from sqlalchemy import Column, Integer, Numeric, String, DateTime, ForeignKey
from datetime import datetime
from sqlalchemy.orm import relationship

class PagoEliminado(Base):
    """
    Modelo que registra los pagos eliminados, guardando
    toda la información original y quién realizó la eliminación.
    """
    __tablename__ = "pagos_eliminados"

    id = Column(Integer, primary_key=True, index=True)
    pago_id_original = Column(Integer, nullable=False)
    alumno_id = Column(ForeignKey("usuarios.id"), nullable=False)
    cuota_id = Column(ForeignKey("cuotas.id"), nullable=True)
    monto_pagado = Column(Numeric(10, 2), nullable=False)
    metodo = Column(String(30), nullable=False)
    comprobante = Column(String(100), nullable=True)
    fecha_pago = Column(DateTime, nullable=False)
    fecha_eliminacion = Column(DateTime, default=datetime.now)
    eliminado_por = Column(ForeignKey("usuarios.id"), nullable=False)
    motivo = Column(String(255), nullable=True)

    # Relaciones
    alumno = relationship("User", foreign_keys=[alumno_id])
    eliminador = relationship("User", foreign_keys=[eliminado_por])

    def __init__(self, pago, eliminado_por, motivo=None):
        """
        Crea un registro a partir de un objeto Pago eliminado.
        Guarda automáticamente la información clave.
        """
        self.pago_id_original = pago.id
        self.alumno_id = pago.alumno_id
        self.cuota_id = pago.cuota_id
        self.monto_pagado = pago.monto_pagado
        self.metodo = pago.metodo
        self.comprobante = pago.comprobante
        self.fecha_pago = pago.fecha_pago
        self.eliminado_por = eliminado_por
        self.motivo = motivo
