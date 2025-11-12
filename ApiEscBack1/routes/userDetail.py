from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.db import get_db
from models.userDetail import UserDetail
from schemas.userDetail import InputUserDetail, UserDetailUpdate, UserDetailOut
from auth.seguridad import obtener_usuario_desde_token, solo_admin
from typing import List

user_detail = APIRouter(prefix="/userdetail", tags=["UserDetail"])


# Obtener el detalle del usuario logueado
@user_detail.get("/me", response_model=UserDetailOut)
def obtener_mi_detalle(
    payload: dict = Depends(obtener_usuario_desde_token),
    db: Session = Depends(get_db)
):
    user_id = int(payload.get("sub"))
    detalle = db.query(UserDetail).filter(UserDetail.user_id == user_id).first()
    if not detalle:
        raise HTTPException(status_code=404, detail="No se encontró detalle del usuario")
    return detalle

# Obtener un detalle por ID (solo Admin/Preceptor)
@user_detail.get("/{user_id}", response_model=UserDetailOut)
def obtener_detalle_por_id(
    user_id: int,
    payload: dict = Depends(solo_admin),
    db: Session = Depends(get_db)
):
    detalle = db.query(UserDetail).filter(UserDetail.user_id == user_id).first()
    if not detalle:
        raise HTTPException(status_code=404, detail="Detalle no encontrado")
    return detalle

# Actualizar un detalle de usuario
@user_detail.patch("/{user_id}", response_model=dict)
def actualizar_detalle(
    user_id: int,
    cambios: UserDetailUpdate,
    payload: dict = Depends(obtener_usuario_desde_token),
    db: Session = Depends(get_db)
):
    detalle = db.query(UserDetail).filter(UserDetail.user_id == user_id).first()
    if not detalle:
        raise HTTPException(status_code=404, detail="Detalle no encontrado")

    # Solo Admin o el propio usuario pueden editar
    if payload["type"] != "Admin" and int(payload["sub"]) != user_id:
        raise HTTPException(status_code=403, detail="No autorizado")

    datos_a_actualizar = cambios.dict(exclude_unset=True)
    if payload["type"] != "Admin":
        datos_a_actualizar.pop("type", None)  # evitar cambiar tipo

    for campo, valor in datos_a_actualizar.items():
        setattr(detalle, campo, valor)

    db.commit()
    db.refresh(detalle)
    return {"msg": "Actualizado correctamente"}

# Crear un detalle (solo Admin)
@user_detail.post("/", response_model=UserDetailOut, status_code=status.HTTP_201_CREATED)
def crear_detalle(
    detalle_in: InputUserDetail,
    payload: dict = Depends(solo_admin),
    db: Session = Depends(get_db)
):
    existe_dni = db.query(UserDetail).filter(UserDetail.dni == detalle_in.dni).first()
    if existe_dni:
        raise HTTPException(status_code=400, detail="DNI duplicado")

    existe_email = db.query(UserDetail).filter(UserDetail.email == detalle_in.email).first()
    if existe_email:
        raise HTTPException(status_code=400, detail="Email duplicado")

    nuevo_detalle = UserDetail(**detalle_in.dict())
    db.add(nuevo_detalle)
    db.commit()
    db.refresh(nuevo_detalle)
    return nuevo_detalle

# Eliminar un detalle (solo Admin)
@user_detail.delete("/{user_id}", status_code=204)
def eliminar_detalle(
    user_id: int,
    payload: dict = Depends(solo_admin),
    db: Session = Depends(get_db)
):
    detalle = db.query(UserDetail).filter(UserDetail.user_id == user_id).first()
    if not detalle:
        raise HTTPException(status_code=404, detail="Detalle no encontrado")

    db.delete(detalle)
    db.commit()
    return {"msg": "Detalle eliminado"}
