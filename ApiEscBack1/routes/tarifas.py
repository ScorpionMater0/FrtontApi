# routes/tarifas.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.db import get_db
from models.tarifa import Tarifa
from schemas.tarifa import TarifaBase, TarifaCreate, TarifaOut
from typing import List
from datetime import date

tarifas = APIRouter(prefix="/tarifas", tags=["Tarifas"])

@tarifas.post("/", response_model=TarifaOut, status_code=status.HTTP_201_CREATED)
def crear_tarifa(data: TarifaCreate, db: Session = Depends(get_db)):
    tarifa = Tarifa(
        monto_mensual=data.monto_mensual,
        vigente_desde=data.vigente_desde,
        vigente_hasta=data.vigente_hasta,
        creado_por=data.creado_por
    )
    db.add(tarifa)
    db.commit()
    db.refresh(tarifa)
    return tarifa


@tarifas.get("/vigente", response_model=TarifaOut)
def obtener_tarifa_vigente(db: Session = Depends(get_db)):
    hoy = date.today()
    tarifa = (
        db.query(Tarifa)
        .filter(Tarifa.vigente_desde <= hoy)
        .filter((Tarifa.vigente_hasta == None) | (Tarifa.vigente_hasta >= hoy))
        .order_by(Tarifa.vigente_desde.desc())
        .first()
    )
    if not tarifa:
        raise HTTPException(status_code=404, detail="No hay tarifa vigente registrada")
    return tarifa


@tarifas.get("/", response_model=List[TarifaOut])
def listar_tarifas(db: Session = Depends(get_db)):
    return db.query(Tarifa).order_by(Tarifa.vigente_desde.desc()).all()
