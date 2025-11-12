# models/tarifa.py
from config.db import Base
from sqlalchemy import Column, Integer, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship

class Tarifa(Base):
    __tablename__ = "tarifas"

    id = Column(Integer, primary_key=True, index=True)
    monto_mensual = Column(Numeric(10, 2), nullable=False)
    vigente_desde = Column(Date, nullable=False)
    vigente_hasta = Column(Date, nullable=True)
    creado_por = Column(ForeignKey("usuarios.id"))

    # Relaciones
    creador = relationship("User", back_populates="tarifas_creadas")

    def __init__(self, monto_mensual, vigente_desde, vigente_hasta=None, creado_por=None):
        self.monto_mensual = monto_mensual
        self.vigente_desde = vigente_desde
        self.vigente_hasta = vigente_hasta
        self.creado_por = creado_por
