from config.db import engine, Base
from models.user import User
from models.userDetail import UserDetail
from models.tarifa import Tarifa
from models.cuota import Cuota
from models.pago import Pago
from models.pagoEliminado import PagoEliminado
from models.notificacionPago import NotificacionPago


def init_db():
    """
    Crea todas las tablas de la base de datos si no existen.
    Se ejecuta automáticamente al iniciar FastAPI (desde main.py).
    """
    try:
        Base.metadata.create_all(bind=engine, tables=[
            User.__table__,
            UserDetail.__table__,
            Tarifa.__table__,
            Cuota.__table__,
            Pago.__table__,
            PagoEliminado.__table__,
            NotificacionPago.__table__,
        ])
        print("✅ Base de datos inicializada correctamente.")
    except Exception as e:
        print(f"⚠️ Error al inicializar la base de datos: {e}")
