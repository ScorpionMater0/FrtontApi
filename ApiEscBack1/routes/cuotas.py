# routes/cuotas.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta
from config.db import get_db
from models.cuota import Cuota
from models.tarifa import Tarifa
from schemas.cuota import CuotaBase, CuotaOut
from typing import List

cuotas = APIRouter(prefix="/cuotas", tags=["Cuotas"])

# Obtener la tarifa vigente
def get_tarifa_vigente(db: Session):
    hoy = date.today()
    return (
        db.query(Tarifa)
        .filter(Tarifa.vigente_desde <= hoy)
        .filter((Tarifa.vigente_hasta == None) | (Tarifa.vigente_hasta >= hoy))
        .order_by(Tarifa.vigente_desde.desc())
        .first()
    )

# Crear una nueva cuota
@cuotas.post("/", response_model=CuotaOut)
def generar_cuota(data: CuotaBase, db: Session = Depends(get_db)):
    tarifa = get_tarifa_vigente(db)
    if not tarifa:
        raise HTTPException(status_code=404, detail="No hay tarifa vigente")

    nueva = Cuota(
        alumno_id=data.alumno_id,
        periodo=data.periodo,
        fecha_vencimiento=data.fecha_vencimiento,
        monto_base=tarifa.monto_mensual,
        ajuste_anterior=data.ajuste_anterior,
        monto_a_pagar=data.monto_a_pagar,
    )

    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

# Listar todas las cuotas
@cuotas.get("/", response_model=List[CuotaOut])
def listar_cuotas(db: Session = Depends(get_db)):
    return db.query(Cuota).order_by(Cuota.id.desc()).all()
