from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Usuario

router = APIRouter(prefix="/api/admin/usuarios", tags=["Admin Usuarios"])


@router.get("")
def listar_usuarios_admin(db: Session = Depends(get_db)):
    usuarios = (
        db.query(Usuario)
        .options(
            joinedload(Usuario.rol),
            joinedload(Usuario.taller)
        )
        .order_by(Usuario.id.asc())
        .all()
    )

    resultado = []

    for u in usuarios:
        nombre_mostrar = u.nombre or "Sin nombre"

        rol_nombre = "Cliente"
        if u.rol and u.rol.nombre:
            nombre_rol = u.rol.nombre.strip().lower()
            if nombre_rol == "taller":
                rol_nombre = "Taller"
            elif nombre_rol == "administrador":
                rol_nombre = "Administrador"

        estado = "Activo" if u.activo else "Inactivo"
        inicial = nombre_mostrar[0].upper() if nombre_mostrar else "U"
        creado = u.fecha_registro.isoformat() if u.fecha_registro else ""
        telefono = u.telefono or ""

        resultado.append({
            "id": u.id,
            "inicial": inicial,
            "nombre": nombre_mostrar,
            "rol": rol_nombre,
            "estado": estado,
            "email": u.email or "",
            "telefono": telefono,
            "ultimoAcceso": "",
            "creado": creado
        })

    return resultado