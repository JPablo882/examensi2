from app.database import SessionLocal
from app.models import Rol, Usuario, Taller
from app.security import get_password_hash


def get_or_create_role(db, nombre: str) -> Rol:
    rol = db.query(Rol).filter(Rol.nombre == nombre).first()
    if not rol:
        rol = Rol(nombre=nombre)
        db.add(rol)
        db.commit()
        db.refresh(rol)
        print(f"✅ Rol creado: {nombre}")
    else:
        print(f"ℹ️ Rol ya existe: {nombre}")
    return rol


def get_or_create_user(
    db,
    *,
    nombre: str,
    email: str,
    telefono: str,
    password: str,
    rol_nombre: str,
    activo: bool = True
) -> Usuario:
    rol = db.query(Rol).filter(Rol.nombre == rol_nombre).first()
    if not rol:
        raise ValueError(f"No existe el rol: {rol_nombre}")

    usuario = db.query(Usuario).filter(Usuario.email == email).first()

    if not usuario:
        usuario = Usuario(
            nombre=nombre,
            email=email,
            telefono=telefono,
            password_hash=get_password_hash(password),
            activo=activo,
            rol_id=rol.id
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        print(f"✅ Usuario creado: {email} ({rol_nombre})")
    else:
        usuario.nombre = nombre
        usuario.telefono = telefono
        usuario.password_hash = get_password_hash(password)
        usuario.activo = activo
        usuario.rol_id = rol.id
        db.commit()
        db.refresh(usuario)
        print(f"♻️ Usuario actualizado: {email} ({rol_nombre})")

    return usuario


def get_or_create_taller(
    db,
    *,
    usuario_id: int,
    nombre_taller: str,
    direccion: str,
    ubicacion: str,
    telefono: str,
    email: str,
    estado: str = "activo"
) -> Taller:
    taller = db.query(Taller).filter(Taller.usuario_id == usuario_id).first()

    if not taller:
        taller = Taller(
            usuario_id=usuario_id,
            nombre_taller=nombre_taller,
            direccion=direccion,
            ubicacion=ubicacion,
            telefono=telefono,
            email=email,
            estado=estado
        )
        db.add(taller)
        db.commit()
        db.refresh(taller)
        print(f"✅ Taller creado: {nombre_taller}")
    else:
        taller.nombre_taller = nombre_taller
        taller.direccion = direccion
        taller.ubicacion = ubicacion
        taller.telefono = telefono
        taller.email = email
        taller.estado = estado
        db.commit()
        db.refresh(taller)
        print(f"♻️ Taller actualizado: {nombre_taller}")

    return taller


def main():
    db = SessionLocal()
    try:
        print("=== Iniciando seed de datos ===")

        # Roles base
        get_or_create_role(db, "administrador")
        get_or_create_role(db, "taller")
        get_or_create_role(db, "cliente")

        # Admin inicial
        get_or_create_user(
            db,
            nombre="Administrador Principal",
            email="dbanegas205@gmail.com",
            telefono="78075594",
            password="1234",
            rol_nombre="administrador",
            activo=True
        )

        # Cliente demo
        get_or_create_user(
            db,
            nombre="Cliente Demo",
            email="cliente@gmail.com",
            telefono="70000001",
            password="1234",
            rol_nombre="cliente",
            activo=True
        )

        # Actualizar/completar taller 1 ya existente
        usuario_taller_1 = get_or_create_user(
            db,
            nombre="Juan Pérez",
            email="taller1@gmail.com",
            telefono="78546215",
            password="1234",
            rol_nombre="taller",
            activo=True
        )

        get_or_create_taller(
            db,
            usuario_id=usuario_taller_1.id,
            nombre_taller="Taller JP",
            direccion="Sin dirección",
            ubicacion="Sin ubicación",
            telefono="78546215",
            email="sinemail@taller.com",
            estado="activo"
        )

        # Actualizar/completar taller 2 ya existente
        usuario_taller_2 = get_or_create_user(
            db,
            nombre="Carlos",
            email="carlos@gmail.com",
            telefono="78546214",
            password="1234",
            rol_nombre="taller",
            activo=True
        )

        get_or_create_taller(
            db,
            usuario_id=usuario_taller_2.id,
            nombre_taller="CarlosJuriol",
            direccion="Av. Grigota",
            ubicacion="Santa Cruz",
            telefono="78546214",
            email="carlos@gmail.com",
            estado="activo"
        )

        print("=== Seed completado correctamente ===")

    except Exception as e:
        db.rollback()
        print(f"❌ Error durante el seed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()