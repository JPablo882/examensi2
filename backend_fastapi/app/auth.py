from passlib.context import CryptContext

# 🔐 Configuración de hash (recomendado)
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# 🔍 Verificar contraseña
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# 🔒 Generar hash
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)