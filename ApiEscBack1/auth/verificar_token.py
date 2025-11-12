import jwt

# Este es el token que generaste y recibiste en Postman
token = "tu_token_aqui"
# Esta debe ser EXACTAMENTE la misma clave usada en tu clase Seguridad
secret = "tu_clave_secreta"
try:
    payload = jwt.decode(token, secret, algorithms=["HS256"])
    print("✅ Token válido. Payload:")
    print(payload)
except jwt.ExpiredSignatureError:
    print("❌ Token expirado.")
except jwt.InvalidTokenError as e:
    print("❌ Token inválido:", str(e))
except Exception as e:
    print("❌ Error general:", str(e))
