from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from datetime import date, timedelta, datetime
from typing import List

from config.db import get_db
from models.cuota import Cuota
from models.notificacionPago import NotificacionPago
from models.user import User
from schemas.notificacionPago import NotificacionPagoOut
from auth.seguridad import solo_admin

notificaciones = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])

# 📆 Generar recordatorios automáticos de vencimiento
@notificaciones.post("/recordatorios", response_model=List[NotificacionPagoOut])
def generar_recordatorios(db: Session = Depends(get_db), payload: dict = Depends(solo_admin)):
    hoy = date.today()
    fecha_objetivo = hoy + timedelta(days=7)

    cuotas_proximas = (
        db.query(Cuota)
        .options(joinedload(Cuota.alumno).joinedload(User.userdetail))
        .filter(Cuota.fecha_vencimiento == fecha_objetivo)
        .filter(Cuota.notificada == False)
        .all()
    )

    if not cuotas_proximas:
        raise HTTPException(status_code=404, detail="No hay cuotas próximas a vencer.")

    notifs = []

    for cuota in cuotas_proximas:
        alumno = cuota.alumno.userdetail if cuota.alumno and cuota.alumno.userdetail else None
        nombre_alumno = f"{alumno.firstName} {alumno.lastName}" if alumno else f"ID {cuota.alumno_id}"

        mensaje_alumno = (
            f"Recordatorio: Tu cuota del período {cuota.periodo} vence el "
            f"{cuota.fecha_vencimiento.strftime('%d/%m/%Y')}. Monto a pagar: ${float(cuota.monto_a_pagar):,.2f}"
        )
        mensaje_admin = (
            f"El alumno {nombre_alumno} tiene una cuota próxima a vencer el "
            f"{cuota.fecha_vencimiento.strftime('%d/%m/%Y')}."
        )

        notif_alumno = NotificacionPago(
            alumno_id=cuota.alumno_id,
            cuota_id=cuota.id,
            tipo="recordatorio_vencimiento",
            destinatario="alumno",
            mensaje=mensaje_alumno
        )
        notif_admin = NotificacionPago(
            alumno_id=cuota.alumno_id,
            cuota_id=cuota.id,
            tipo="recordatorio_vencimiento",
            destinatario="admin",
            mensaje=mensaje_admin
        )

        db.add_all([notif_alumno, notif_admin])
        cuota.notificada = True
        notifs.extend([notif_alumno, notif_admin])

    db.commit()
    print(f"✅ {len(notifs)} notificaciones generadas correctamente.")
    return notifs


# 📋 Listar notificaciones recientes (extendido con nombre y periodo)
@notificaciones.get("/listar", response_model=List[NotificacionPagoOut])
def listar_notificaciones(db: Session = Depends(get_db), payload: dict = Depends(solo_admin)):
    """
    Devuelve todas las notificaciones enviadas (ordenadas por fecha descendente),
    incluyendo nombre del alumno y período de la cuota.
    Solo accesible por Admin.
    """
    notifs = (
        db.query(NotificacionPago)
        .options(
            joinedload(NotificacionPago.alumno).joinedload(User.userdetail),
            joinedload(NotificacionPago.cuota)
        )
        .order_by(NotificacionPago.fecha_envio.desc())
        .limit(100)
        .all()
    )

    if not notifs:
        raise HTTPException(status_code=404, detail="No hay notificaciones registradas.")

    salida = []
    for n in notifs:
        alumno = n.alumno.userdetail if n.alumno and n.alumno.userdetail else None
        nombre_alumno = f"{alumno.firstName} {alumno.lastName}" if alumno else f"ID {n.alumno_id}"
        periodo = n.cuota.periodo if n.cuota else "Desconocido"

        salida.append({
            "id": n.id,
            "alumno_id": n.alumno_id,
            "cuota_id": n.cuota_id,
            "tipo": n.tipo,
            "destinatario": n.destinatario,
            "mensaje": n.mensaje,
            "fecha_envio": n.fecha_envio,
            "alumno_nombre": nombre_alumno,
            "periodo": periodo,
        })

    return salida
