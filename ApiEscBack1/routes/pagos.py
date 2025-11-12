from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from typing import List

from config.db import get_db
from auth.seguridad import obtener_usuario_desde_token, solo_admin
from models.pago import Pago
from models.cuota import Cuota
from models.user import User
from models.pagoEliminado import PagoEliminado
from models.notificacionPago import NotificacionPago
from schemas.pago import PagoBase, PagoOut, PagoEliminadoIn, PagoEliminadoOut
from psycopg2 import IntegrityError


pagos = APIRouter(prefix="/pagos", tags=["Pagos"])

# 📌 ADMIN o ALUMNO: Registrar nuevo pago flexible (con notificación)
@pagos.post("/nuevo", response_model=dict)
def nuevo_pago(
    data: PagoBase,
    db: Session = Depends(get_db),
    payload: dict = Depends(obtener_usuario_desde_token)
):
    try:
        # Solo Admin o Alumno
        if payload["type"] not in ["Admin", "Alumno"]:
            raise HTTPException(status_code=403, detail="No autorizado para registrar pagos")

        alumno_id = data.alumno_id or int(payload["sub"])
        monto_pagado = float(data.monto_pagado)

        cuota = db.query(Cuota).filter_by(id=data.cuota_id, alumno_id=alumno_id).first()
        if not cuota:
            raise HTTPException(status_code=404, detail="Cuota no encontrada")

        # Calcular saldo evitando negativos
        cuota.monto_pagado += monto_pagado
        cuota.saldo_pendiente = max(0, float(cuota.monto_a_pagar) - float(cuota.monto_pagado))

        # Actualizar estado según saldo
        if cuota.saldo_pendiente == 0:
            cuota.estado = "pagada"
        elif 0 < cuota.saldo_pendiente < float(cuota.monto_a_pagar):
            cuota.estado = "parcial"
        else:
            cuota.estado = "pendiente"

        # Crear registro del pago
        nuevo = Pago(
            alumno_id=alumno_id,
            cuota_id=cuota.id,
            monto_pagado=monto_pagado,
            metodo=data.metodo,
            comprobante=data.comprobante,
            registrado_por=payload["sub"]
        )
        db.add(nuevo)
        db.commit()

        # 🔔 Crear notificaciones automáticas
        mensaje_alumno = (
            f"Se registró un pago de ${monto_pagado:,.2f} "
            f"para tu cuota del período {cuota.periodo}."
        )
        mensaje_admin = (
            f"El alumno ID {alumno_id} realizó un pago de ${monto_pagado:,.2f} "
            f"para la cuota {cuota.periodo}."
        )

        notif_alumno = NotificacionPago(
            alumno_id=alumno_id,
            cuota_id=cuota.id,
            tipo="pago_registrado",
            destinatario="alumno",
            mensaje=mensaje_alumno
        )
        notif_admin = NotificacionPago(
            alumno_id=alumno_id,
            cuota_id=cuota.id,
            tipo="pago_registrado",
            destinatario="admin",
            mensaje=mensaje_admin
        )

        db.add_all([notif_alumno, notif_admin])
        db.commit()

        return {"message": "Pago registrado y notificaciones enviadas correctamente"}

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error de integridad al registrar pago")
    except Exception as e:
        db.rollback()
        print("Error en nuevo pago:", e)
        raise HTTPException(status_code=500, detail="Error interno del servidor")


# 📌 ADMIN: Eliminar pago y registrar en historial
@pagos.delete("/eliminar/{pago_id}")
def eliminar_pago(
    pago_id: int,
    data: PagoEliminadoIn = None,
    db: Session = Depends(get_db),
    payload: dict = Depends(solo_admin)
):
    pago_obj = db.query(Pago).filter_by(id=pago_id).first()
    if not pago_obj:
        raise HTTPException(status_code=404, detail="Pago no encontrado")

    try:
        motivo = data.motivo if data else None

        # Registrar copia del pago eliminado
        registro = PagoEliminado(pago=pago_obj, eliminado_por=payload["sub"], motivo=motivo)
        db.add(registro)

        # Ajustar saldo en la cuota
        cuota = db.query(Cuota).filter_by(id=pago_obj.cuota_id).first()
        if cuota:
            cuota.monto_pagado -= pago_obj.monto_pagado
            cuota.saldo_pendiente = max(0, float(cuota.monto_a_pagar) - float(cuota.monto_pagado))
            cuota.estado = "pendiente" if cuota.monto_pagado <= 0 else "parcial"

        # 🔔 Registrar notificación por eliminación
        mensaje_admin = (
            f"Se eliminó el pago ID {pago_obj.id} del alumno ID {pago_obj.alumno_id}. "
            f"Monto: ${float(pago_obj.monto_pagado):,.2f}. Motivo: {motivo or 'No especificado'}."
        )
        notif = NotificacionPago(
            alumno_id=pago_obj.alumno_id,
            cuota_id=pago_obj.cuota_id,
            tipo="pago_eliminado",
            destinatario="admin",
            mensaje=mensaje_admin
        )
        db.add(notif)

        # Eliminar el pago original
        db.delete(pago_obj)
        db.commit()
        return {"message": "Pago eliminado, registrado y notificado"}

    except Exception as e:
        db.rollback()
        print("Error al eliminar pago:", e)
        raise HTTPException(status_code=500, detail="Error interno del servidor")


# 📜 ADMIN: Ver historial de pagos eliminados
@pagos.get("/eliminados", response_model=List[PagoEliminadoOut])
def listar_pagos_eliminados(
    db: Session = Depends(get_db),
    payload: dict = Depends(solo_admin)
):
    registros = (
        db.query(PagoEliminado)
        .order_by(PagoEliminado.fecha_eliminacion.desc())
        .all()
    )
    return registros


# 📊 ADMIN: Ver último pago registrado
@pagos.get("/ultimo", response_model=dict)
def obtener_ultimo_pago(
    db: Session = Depends(get_db),
    payload: dict = Depends(solo_admin)
):
    ultimo = (
        db.query(Pago)
        .options(joinedload(Pago.alumno).joinedload(User.userdetail))
        .order_by(Pago.id.desc())
        .first()
    )

    if not ultimo:
        raise HTTPException(status_code=404, detail="No hay pagos registrados")

    return {
        "alumno": f"{ultimo.alumno.userdetail.firstName} {ultimo.alumno.userdetail.lastName}",
        "monto_pagado": float(ultimo.monto_pagado),
        "fecha_pago": ultimo.fecha_pago.strftime("%Y-%m-%d %H:%M"),
        "metodo": ultimo.metodo,
    }


# 👤 ALUMNO: Ver sus propios pagos
@pagos.get("/mis", response_model=List[PagoOut])
def ver_mis_pagos(
    db: Session = Depends(get_db),
    payload: dict = Depends(obtener_usuario_desde_token)
):
    if payload["type"] != "Alumno":
        raise HTTPException(status_code=403, detail="Solo los alumnos pueden ver sus pagos")

    pagos_alumno = (
        db.query(Pago)
        .options(joinedload(Pago.cuota))
        .filter(Pago.alumno_id == int(payload["sub"]))
        .order_by(Pago.fecha_pago.desc())
        .all()
    )

    return [
        {
            "id": p.id,
            "monto_pagado": float(p.monto_pagado),
            "fecha_pago": p.fecha_pago.strftime("%Y-%m-%d"),
            "metodo": p.metodo,
            "periodo": p.cuota.periodo if p.cuota else "Sin período"
        }
        for p in pagos_alumno
    ]


# ⚙️ ADMIN: Editar pago parcialmente
@pagos.patch("/editar/{pago_id}", response_model=dict)
def editar_pago_parcial(
    pago_id: int,
    datos: dict,
    db: Session = Depends(get_db),
    payload: dict = Depends(solo_admin)
):
    pago_existente = db.query(Pago).filter_by(id=pago_id).first()
    if not pago_existente:
        raise HTTPException(status_code=404, detail="Pago no encontrado")

    for campo, valor in datos.items():
        if hasattr(pago_existente, campo):
            setattr(pago_existente, campo, valor)

    db.commit()
    return {"message": "Pago actualizado correctamente"}
