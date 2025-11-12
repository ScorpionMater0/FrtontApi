# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from routes.user import user
from routes.tarifas import tarifas
from routes.cuotas import cuotas
from routes.pagos import pagos          
from routes.notificaciones import notificaciones


from config.init_db import init_db


api_escu = FastAPI(title="ApiEscuela", version="2.0")

# Middleware CORS
api_escu.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # podés restringir a ["http://localhost:5173"] si querés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


init_db()


api_escu.include_router(user)
api_escu.include_router(tarifas)
api_escu.include_router(cuotas)
api_escu.include_router(pagos)
api_escu.include_router(notificaciones)


@api_escu.get("/")
def root():
    return {"message": "API Escuela funcionando correctamente 🚀"}
