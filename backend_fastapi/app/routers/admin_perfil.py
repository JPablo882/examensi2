from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Usuario

router = APIRouter(prefix="/api/admin/perfil", tags=["Perfil Administrador"])

@router.get("/")
def obtener_perfil_admin(
    admin_email: str = Query(...),
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.email == admin_email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "email": usuario.email,
        "telefono": usuario.telefono or "",
        "direccion": getattr(usuario, 'direccion', ''),
        "ciudad": getattr(usuario, 'ciudad', ''),
        "apellidos": getattr(usuario, 'apellidos', ''),
        "rol": usuario.rol.nombre if usuario.rol else ""
    }

@router.put("/actualizar")
def actualizar_perfil_admin(
    admin_email: str = Query(...),
    datos: dict = None,
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.email == admin_email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    if datos:
        if 'nombre' in datos and datos['nombre']:
            usuario.nombre = datos['nombre']
        
        if 'apellidos' in datos and datos['apellidos']:
            usuario.apellidos = datos['apellidos']
        
        if 'telefono' in datos and datos['telefono']:
            usuario.telefono = datos['telefono']
        
        if 'direccion' in datos and datos['direccion']:
            usuario.direccion = datos['direccion']
        
        if 'ciudad' in datos and datos['ciudad']:
            usuario.ciudad = datos['ciudad']
    
    db.commit()
    
    return {
        "message": "Perfil actualizado correctamente",
        "nombre": usuario.nombre,
        "apellidos": getattr(usuario, 'apellidos', ''),
        "telefono": usuario.telefono,
        "direccion": getattr(usuario, 'direccion', ''),
        "ciudad": getattr(usuario, 'ciudad', ''),
        "email": usuario.email
    }