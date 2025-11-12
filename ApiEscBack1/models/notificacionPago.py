# models/notificacion_pago.py
from config.db import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
import datetime

class NotificacionPago(Base):
    __tablename__ = "notificaciones_pago"

    id = Column(Integer, primary_key=True, index=True)
    alumno_id = Column(ForeignKey("usuarios.id"), nullable=False)
    cuota_id = Column(ForeignKey("cuotas.id"), nullable=False)
    tipo = Column(String(50), nullable=False)  # recordatorio_vencimiento, deuda, pago_registrado
    fecha_envio = Column(DateTime, default=datetime.datetime.now)
    destinatario = Column(String(20), nullable=False)  # alumno, admin
    mensaje = Column(String(255), nullable=False)

    def __init__(self, alumno_id, cuota_id, tipo, destinatario, mensaje):
        self.alumno_id = alumno_id
        self.cuota_id = cuota_id
        self.tipo = tipo
        self.destinatario = destinatario
        self.mensaje = mensaje
