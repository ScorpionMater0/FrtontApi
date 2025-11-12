from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import joinedload, Session
from config.db import get_db
from auth.seguridad import obtener_usuario_desde_token, Seguridad, solo_admin
from models.user import User
from models.userDetail import UserDetail
from models.pago import Pago
from schemas.user import (
    InputLogin,
    InputUser,
    UserOut,
    PaginatedUsersOut,
    PaginatedFilteredBody
)
from typing import List

user = APIRouter(prefix="/user", tags=["User"])

# 📌 Obtener perfil del usuario autenticado
@user.get("/profile", response_model=UserOut)
def get_own_profile(
    payload: dict = Depends(obtener_usuario_desde_token),
    db: Session = Depends(get_db)
):
    """
    Devuelve el perfil completo del usuario autenticado (User + UserDetail).
    """
    try:
        user_id = int(payload.get("sub"))
        db_user = (
            db.query(User)
            .options(joinedload(User.userdetail))
            .filter(User.id == user_id)
            .first()
        )
        if not db_user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return db_user
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Error al obtener perfil")


#  Listado paginado y filtrado de usuarios (solo Admin)
@user.post("/paginated/filtered-sync", response_model=PaginatedUsersOut)
def get_users_paginated_filtered_sync(
    body: PaginatedFilteredBody,
    payload: dict = Depends(solo_admin),
    db: Session = Depends(get_db)
):
    """
    Retorna una lista paginada y filtrada de usuarios.
    Permite filtrar por nombre, email, username, etc.
    """
    limit = body.limit or 20
    last_seen_id = body.last_seen_id or 0
    search = (body.search or "").strip()

    try:
        q = (
            db.query(User)
            .outerjoin(User.userdetail)
            .options(joinedload(User.userdetail))
        )

        if search:
            like = f"%{search}%"
            q = q.filter(
                (User.username.ilike(like)) |
                (UserDetail.email.ilike(like)) |
                (UserDetail.firstName.ilike(like)) |
                (UserDetail.lastName.ilike(like))
            )

        if last_seen_id > 0:
            q = q.filter(User.id > last_seen_id)

        q = q.order_by(User.id.asc()).limit(limit)

        users_db = q.all()
        next_cursor = users_db[-1].id if users_db else None

        return {
            "users": users_db,
            "next_cursor": next_cursor
        }

    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Error al obtener usuarios")


#  Crear usuario con detalles completos (solo Admin)
@user.post("/register/full")
def crear_usuario_completo(
    user: InputUser,
    payload: dict = Depends(obtener_usuario_desde_token),
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo usuario con su correspondiente UserDetail.
    Solo el administrador puede realizar esta acción.
    """
    if payload["type"] != "Admin":
        raise HTTPException(status_code=403, detail="No tienes permiso para registrar usuarios")

    try:
        existing_username = db.query(User).filter(User.username == user.username).first()
        existing_email = db.query(UserDetail).filter(UserDetail.email == user.email).first()

        if existing_username:
            raise HTTPException(status_code=400, detail="El usuario ya existe")
        if existing_email:
            raise HTTPException(status_code=400, detail="El email ya existe")

        # Crear usuario base
        new_user = User(username=user.username, password=user.password)
        db.add(new_user)
        db.flush()  # 🔹 genera el ID del usuario

        # Crear detalle asociado
        new_detail = UserDetail(
            dni=user.dni,
            firstName=user.firstName,
            lastName=user.lastName,
            type=user.type,
            email=user.email,
            user_id=new_user.id
        )

        db.add(new_detail)
        db.commit()
        db.refresh(new_user)

        return {"msg": "Usuario registrado correctamente"}

    except Exception as e:
        db.rollback()
        print("Error al registrar usuario:", e)
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")


#  Login de usuario
@user.post("/loginUser")
def login_post(userIn: InputLogin, db: Session = Depends(get_db)):
    """
    Autentica a un usuario y devuelve un token JWT,
    sincronizando la respuesta con el formato esperado por el Frontend.
    """
    try:
        user = db.query(User).filter(User.username == userIn.username).first()
        
        if not user or user.password != userIn.password:
            # CORRECCIÓN 1: Usar "status": "error"
            return JSONResponse(
                status_code=401, 
                content={
                    "status": "error", 
                    "message": "Usuario o contraseña incorrectos"
                }
            )

        token = Seguridad.generar_token(user)
        if not token:
            # CORRECCIÓN 2: Usar "status": "error"
            return JSONResponse(
                status_code=401, 
                content={
                    "status": "error", 
                    "message": "Error al generar el token"
                }
            )

        # CORRECCIÓN 3: Usar "status": "success" y la clave "user"
        return JSONResponse(status_code=200, content={
            "status": "success",
            "token": token,
            # Se usa 'user' como clave, y se envía el tipo de usuario.
            "user": {"type": user.userdetail.type if user.userdetail else None} 
        })

    except Exception as e:
        print("Error en login:", e)
        # CORRECCIÓN 4: Usar "status": "error"
        return JSONResponse(
            status_code=500, 
            content={
                "status": "error", 
                "message": "Error interno del servidor"
            }
        )

# 👨‍🎓 Obtener todos los alumnos (solo Admin)
@user.get("/alumnos")
def obtener_alumnos(
    payload: dict = Depends(solo_admin),
    db: Session = Depends(get_db)
):
    """
    Devuelve una lista de todos los alumnos registrados.
    """
    try:
        alumnos = (
            db.query(User)
            .join(UserDetail)
            .filter(UserDetail.type == "Alumno")
            .all()
        )
        return [
            {
                "id": a.id,
                "username": a.username,
                "userdetail": {
                    "firstName": a.userdetail.firstName,
                    "lastName": a.userdetail.lastName,
                    "email": a.userdetail.email,
                    "dni": a.userdetail.dni
                }
            }
            for a in alumnos
        ]
    except Exception as e:
        print("Error al obtener alumnos:", e)
        raise HTTPException(status_code=500, detail="Error al obtener alumnos")

# 🕐 Obtener el último usuario registrado (solo Admin)
@user.get("/ultimo")
def obtener_ultimo_usuario(
    payload: dict = Depends(solo_admin),
    db: Session = Depends(get_db)
):
    """
    Devuelve los datos del último usuario registrado.
    """
    try:
        ultimo = (
            db.query(User)
            .options(joinedload(User.userdetail))
            .order_by(User.id.desc())
            .first()
        )

        if not ultimo or not ultimo.userdetail:
            raise HTTPException(status_code=404, detail="No hay usuarios registrados")

        return {
            "firstName": ultimo.userdetail.firstName,
            "lastName": ultimo.userdetail.lastName
        }

    except Exception as e:
        print("Error al obtener último usuario:", e)
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# ❌ Eliminar un usuario y sus datos asociados (solo Admin)
@user.delete("/{user_id}", response_model=dict)
def eliminar_usuario(
    user_id: int,
    payload: dict = Depends(solo_admin),
    db: Session = Depends(get_db)
):
    """
    Elimina un usuario y todos sus datos asociados (pagos, detalle, etc.).
    """
    try:
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Borrar pagos asociados
        pagos = db.query(Pago).filter(Pago.user_id == user_id).all()
        for pago in pagos:
            db.delete(pago)

        # Borrar detalle asociado
        if db_user.userdetail:
            db.delete(db_user.userdetail)

        # Borrar usuario base
        db.delete(db_user)
        db.commit()

        return {"msg": "Usuario y datos asociados eliminados correctamente"}

    except Exception as e:
        db.rollback()
        print("Error al eliminar usuario:", e)
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
