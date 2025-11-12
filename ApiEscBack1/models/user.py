from config.db import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)

    # Relaciones principales
    userdetail = relationship("UserDetail", back_populates="user", uselist=False)
    cuotas = relationship("Cuota", back_populates="alumno")

    # Relación con pagos
    pagos_alumno = relationship(
        "Pago",
        foreign_keys="[Pago.alumno_id]",
        back_populates="alumno"
    )

    pagos_registrados = relationship(
        "Pago",
        foreign_keys="[Pago.registrado_por]",
        back_populates="registrado"
    )

    # Relación con tarifas
    tarifas_creadas = relationship(
        "Tarifa",
        back_populates="creador"
    )
