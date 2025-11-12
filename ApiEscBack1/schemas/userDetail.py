# schemas/user_detail.py
from pydantic import BaseModel
from typing import Optional, Literal

class InputUserDetail(BaseModel):
    dni: int
    firstName: str
    lastName: str
    type: Literal["Alumno", "Admin"]
    email: str
    anio_lectivo: Optional[int] = None
    estado_academico: Optional[str] = None
    user_id: Optional[int] = None

class UserDetailUpdate(BaseModel):
    dni: Optional[int] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    type: Optional[Literal["Alumno", "Admin"]] = None
    email: Optional[str] = None
    anio_lectivo: Optional[int] = None
    estado_academico: Optional[str] = None

class UserDetailOut(BaseModel):
    id: int
    dni: int
    firstName: str
    lastName: str
    type: str
    email: str
    anio_lectivo: Optional[int] = None
    estado_academico: Optional[str] = None

    class Config:
        from_attributes = True
