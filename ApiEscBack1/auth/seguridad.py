import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Header, Depends
from typing import Dict, Any
from models.user import User
from zoneinfo import ZoneInfo

# Para verificar tipo en dependencias
from fastapi import Request

class Seguridad:
    secret = "tu_clave_secreta"  # ⚠️ En producción, pasalo a variable de entorno

    @classmethod
    def generar_token(cls, user: User) -> str:
        try:
            zona_arg = ZoneInfo("America/Argentina/Buenos_Aires")
            ahora = datetime.now(zona_arg)

            payload = {
                "sub": str(user.id),
                "username": user.username,
                "type": getattr(user.userdetail, "type", None) or "Desconocido",
                "exp": ahora + timedelta(days=1),
                "iat": ahora,
            }
            token = jwt.encode(payload, cls.secret, algorithm="HS256")
            if isinstance(token, bytes):
                token = token.decode("utf-8")
            return token
        except Exception as e:
            print("[ERROR] Al generar token:", e)
            return ""

    @classmethod
    def verificar_token(cls, header: Dict[str, str]) -> Dict[str, Any]:
        if "authorization" not in header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se proporcionó token de autorización."
            )
        try:
            token_type, token = header["authorization"].split(" ")

            if token_type.lower() != "bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Formato de token incorrecto. Se espera 'Bearer <token>'."
                )

            payload = jwt.decode(token, cls.secret, algorithms=["HS256"])
            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expirado.")
        except jwt.DecodeError:
            raise HTTPException(status_code=401, detail="Error al decodificar el token.")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Token inválido.")
        except ValueError:
            raise HTTPException(
                status_code=401,
                detail="Formato de cabecera de autorización incorrecto."
            )
        except Exception as e:
            print("[ERROR] Verificación de token falló:", e)
            raise HTTPException(
                status_code=500,
                detail="Error interno del servidor al verificar el token."
            )

# Dependencia general
async def obtener_usuario_desde_token(authorization: str = Header(...)) -> Dict[str, Any]:
    headers = {"authorization": authorization}
    return Seguridad.verificar_token(headers)

# 👑 Solo admin
async def solo_admin(user=Depends(obtener_usuario_desde_token)):
    if user["type"].lower() != "admin":
        raise HTTPException(status_code=403, detail="Solo admin puede acceder")
    return user

# 🎓 Solo alumno
async def solo_alumno(user=Depends(obtener_usuario_desde_token)):
    if user["type"].lower() != "alumno":
        raise HTTPException(status_code=403, detail="Solo alumnos pueden acceder")
    return user
