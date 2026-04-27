from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Rol, Usuario, Taller
from app.schemas import (
    LoginRequest,
    LoginResponse,
    RegisterTallerRequest,
    RegisterTallerResponse,
    RegisterClienteRequest  # 🔥 IMPORTANTE
)
from app.security import get_password_hash, verify_password

router = APIRouter(prefix="/api/auth", tags=["Auth"])


# 🔐 LOGIN
@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    access_type = data.access_type.strip().lower()

    user = db.query(Usuario).filter(
        Usuario.email == email,
        Usuario.activo == True
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas."
        )

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas."
        )

    rol_nombre = user.rol.nombre.strip().lower() if user.rol else ""

    if access_type == "admin":
        if rol_nombre != "administrador":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Esta cuenta no tiene acceso administrativo."
            )

    elif access_type == "taller":
        if rol_nombre != "taller":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Esta cuenta no tiene acceso de taller."
            )
            
    # 🔥 BUSCAR EL TALLER ASOCIADO AL USUARIO
        taller = db.query(Taller).filter(Taller.usuario_id == user.id).first()
        
        if not taller:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Taller no encontrado para este usuario."
            )
        
        return {
        "message": "Login correcto",
        "user": {
            "id": user.id,
            "nombre": user.nombre,
            "email": user.email,
            "telefono": user.telefono,
            "rol": user.rol.nombre,
          },
           "taller": {  # 🔥 AGREGAR ESTO
            "id": taller.id if taller else None,
            "nombre_taller": taller.nombre_taller if taller else None,
            "email": taller.email if taller else None
          }
        }

    elif access_type == "cliente":
        if rol_nombre != "cliente":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Esta cuenta no tiene acceso de cliente."
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de acceso no válido."
        )

    return {
        "message": "Login correcto",
        "user": {
            "id": user.id,
            "nombre": user.nombre,
            "email": user.email,
            "telefono": user.telefono,
            "rol": user.rol.nombre,
        }
    }


# 🏭 REGISTRO TALLER
@router.post(
    "/register-taller",
    response_model=RegisterTallerResponse,
    status_code=status.HTTP_201_CREATED
)
def register_taller(data: RegisterTallerRequest, db: Session = Depends(get_db)):
    nombre_completo = data.nombreCompleto.strip()
    email_usuario = data.email.strip().lower()
    telefono = data.telefono.strip()
    nombre_taller = data.nombreTaller.strip()
    direccion = data.direccion.strip()
    ubicacion = data.ubicacion.strip()
    email_taller = data.emailTaller.strip().lower()

    if (
        not nombre_completo
        or not email_usuario
        or not telefono
        or not nombre_taller
        or not direccion
        or not ubicacion
        or not email_taller
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Todos los campos son obligatorios."
        )

    if data.password != data.confirmPassword:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Las contraseñas no coinciden."
        )

    if not data.aceptaTerminos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debes aceptar los términos y condiciones."
        )

    existe_usuario = db.query(Usuario).filter(Usuario.email == email_usuario).first()
    if existe_usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con ese email."
        )

    rol_taller = db.query(Rol).filter(Rol.nombre == "taller").first()
    if not rol_taller:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No existe el rol taller."
        )

    nuevo_usuario = Usuario(
        nombre=nombre_completo,
        email=email_usuario,
        telefono=telefono,
        password_hash=get_password_hash(data.password),
        activo=True,
        rol_id=rol_taller.id
    )

    db.add(nuevo_usuario)
    db.flush()

    nuevo_taller = Taller(
        usuario_id=nuevo_usuario.id,
        nombre_taller=nombre_taller,
        direccion=direccion,
        ubicacion=ubicacion,
        telefono=telefono,
        email=email_taller,
        estado="activo"
    )

    db.add(nuevo_taller)
    db.commit()
    db.refresh(nuevo_usuario)

    return {
        "message": "Taller registrado correctamente.",
        "user": {
            "id": nuevo_usuario.id,
            "nombre": nuevo_usuario.nombre,
            "email": nuevo_usuario.email,
            "telefono": nuevo_usuario.telefono,
            "rol": rol_taller.nombre,
        }
    }


# 👤 REGISTRO CLIENTE (🔥 CORREGIDO)
# 👤 REGISTRO CLIENTE (🔥 FIX REAL)
@router.post("/register-cliente", status_code=status.HTTP_201_CREATED)
def register_cliente(data: RegisterClienteRequest, db: Session = Depends(get_db)):

    nombre = data.nombre.strip()
    telefono = data.telefono.strip()
    email = data.email.strip().lower()

    existe_usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if existe_usuario:
        raise HTTPException(
            status_code=400,
            detail="El usuario ya existe"
        )

    rol_cliente = db.query(Rol).filter(Rol.nombre == "cliente").first()
    if not rol_cliente:
        raise HTTPException(
            status_code=500,
            detail="No existe el rol cliente"
        )

    nuevo_usuario = Usuario(
        nombre=nombre,             # ✅ REAL
        email=email,
        telefono=telefono,         # ✅ REAL
        password_hash=get_password_hash(data.password),
        activo=True,
        rol_id=rol_cliente.id
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return {
        "message": "Cliente registrado correctamente",
        "user": {
            "id": nuevo_usuario.id,
            "nombre": nuevo_usuario.nombre,
            "email": nuevo_usuario.email,
            "telefono": nuevo_usuario.telefono,
            "rol": "cliente"
        }
    }