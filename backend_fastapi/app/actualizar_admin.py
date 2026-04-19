from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Rol, Usuario
from app.auth import get_password_hash


def main():
    db: Session = SessionLocal()

    try:
        email_admin = "dbanegas205@gmail.com"
        nueva_password = "1234"

        rol_admin = db.query(Rol).filter(Rol.nombre.ilike("Administrador")).first()

        if not rol_admin:
            rol_admin = Rol(nombre="Administrador")
            db.add(rol_admin)
            db.commit()
            db.refresh(rol_admin)
            print("Rol Administrador creado correctamente.")
        else:
            print("El rol Administrador ya existe.")

        usuario = db.query(Usuario).filter(Usuario.email.ilike(email_admin)).first()

        if not usuario:
            print("No existe un usuario con ese email.")
            return

        usuario.password = get_password_hash(nueva_password)
        usuario.rol_id = rol_admin.id
        usuario.is_staff = True
        usuario.is_superuser = True
        usuario.is_active = True

        db.commit()
        db.refresh(usuario)

        print("Usuario actualizado correctamente como administrador FastAPI.")
        print(f"Email: {usuario.email}")
        print("Password: 1234")

    except Exception as e:
        db.rollback()
        print("Error al actualizar administrador:", str(e))
    finally:
        db.close()


if __name__ == "__main__":
    main()