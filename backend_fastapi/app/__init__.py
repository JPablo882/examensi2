from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Rol

def init_roles():
    db: Session = SessionLocal()

    roles = ["administrador", "taller", "cliente"]

    for rol_nombre in roles:
        rol_existente = db.query(Rol).filter(Rol.nombre == rol_nombre).first()
        if not rol_existente:
            nuevo_rol = Rol(nombre=rol_nombre)
            db.add(nuevo_rol)
            print(f"✅ Rol creado automáticamente: {rol_nombre}")

    db.commit()
    db.close()