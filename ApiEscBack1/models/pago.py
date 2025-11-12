from config.db import Base
from sqlalchemy import Column, Integer, Numeric, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime

class Pago(Base):
    __tablename__ = "pagos"

    id = Column(Integer, primary_key=True, index=True)
    alumno_id = Column(ForeignKey("usuarios.id"), nullable=False)
    cuota_id = Column(ForeignKey("cuotas.id"), nullable=False)
    monto_pagado = Column(Numeric(10, 2), nullable=False)
    metodo = Column(String(30), nullable=False)
    comprobante = Column(String(100), nullable=True)
    fecha_pago = Column(DateTime, default=datetime.datetime.now)
    registrado_por = Column(ForeignKey("usuarios.id"), nullable=False)

    # Relaciones
    alumno = relationship("User", foreign_keys=[alumno_id], back_populates="pagos_alumno")
    cuota = relationship("Cuota", back_populates="pagos")
    registrado = relationship("User", foreign_keys=[registrado_por])