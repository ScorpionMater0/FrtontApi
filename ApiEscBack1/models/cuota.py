# models/cuota.py
from config.db import Base
from sqlalchemy import Column, Integer, String, Date, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import relationship

class Cuota(Base):
    __tablename__ = "cuotas"

    id = Column(Integer, primary_key=True, index=True)
    alumno_id = Column(ForeignKey("usuarios.id"), nullable=False)
    periodo = Column(String(7), nullable=False)  # Formato 'YYYY-MM'
    fecha_vencimiento = Column(Date, nullable=False)
    monto_base = Column(Numeric(10, 2), nullable=False)
    ajuste_anterior = Column(Numeric(10, 2), default=0)
    monto_a_pagar = Column(Numeric(10, 2), nullable=False)
    monto_pagado = Column(Numeric(10, 2), default=0)
    saldo_pendiente = Column(Numeric(10, 2), default=0)
    estado = Column(String(20), default="pendiente")  # pendiente, pagada, parcial, vencida
    notificada = Column(Boolean, default=False)

    # Relaciones
    alumno = relationship("User", back_populates="cuotas")
    pagos = relationship("Pago", back_populates="cuota", cascade="all, delete-orphan")

    def __init__(self, alumno_id, periodo, fecha_vencimiento, monto_base, monto_a_pagar, ajuste_anterior=0):
        self.alumno_id = alumno_id
        self.periodo = periodo
        self.fecha_vencimiento = fecha_vencimiento
        self.monto_base = monto_base
        self.monto_a_pagar = monto_a_pagar
        self.ajuste_anterior = ajuste_anterior
