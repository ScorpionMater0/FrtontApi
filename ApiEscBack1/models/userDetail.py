from config.db import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class UserDetail(Base):
    __tablename__ = "userDetail"

    id = Column(Integer, primary_key=True, index=True)
    dni = Column(Integer, nullable=False, unique=True)
    firstName = Column(String, nullable=False)
    lastName = Column(String, nullable=False)
    type = Column(String(50), nullable=False)  # "Alumno" o "Admin"
    email = Column(String(80), nullable=False, unique=True)
    anio_lectivo = Column(Integer, nullable=True)
    estado_academico = Column(String(30), nullable=True)

    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    # Relaciones
    user = relationship("User", back_populates="userdetail", uselist=False)

    def __init__(self, dni, firstName, lastName, type, email, user_id=None):
        self.dni = dni
        self.firstName = firstName
        self.lastName = lastName
        self.type = type
        self.email = email
        self.user_id = user_id