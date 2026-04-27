from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Taller, Usuario

router = APIRouter(prefix="/api/perfil/taller", tags=["Perfil Taller"])

@router.get("/{taller_email}")
def obtener_perfil_taller(taller_email: str, db: Session = Depends(get_db)):
    taller = db.query(Taller).filter(Taller.email == taller_email).first()
    
    if not taller:
        raise HTTPException(status_code=404, detail="Taller no encontrado")
    
    usuario = db.query(Usuario).filter(Usuario.id == taller.usuario_id).first()
    
    return {
        "id": taller.id,
        "nombre_taller": taller.nombre_taller,
        "direccion": taller.direccion,
        "ubicacion": taller.ubicacion,
        "telefono": taller.telefono,
        "email": taller.email,
        "estado": taller.estado,
        "encargado": usuario.nombre if usuario else "No definido",
        "email_encargado": usuario.email if usuario else "",
        "telefono_encargado": usuario.telefono if usuario else ""
    }


# ==================== NUEVO ENDPOINT PARA ACTUALIZAR PERFIL ====================

@router.put("/actualizar")
def actualizar_perfil_taller(
    taller_email: str = Query(...),
    datos: dict = None,
    db: Session = Depends(get_db)
):
    """Actualizar perfil del taller - solo actualiza los campos enviados"""
    
    # Buscar el taller por email
    taller = db.query(Taller).filter(Taller.email == taller_email).first()
    if not taller:
        raise HTTPException(status_code=404, detail="Taller no encontrado")
    
    # Buscar el usuario asociado (encargado)
    usuario = db.query(Usuario).filter(Usuario.id == taller.usuario_id).first()
    
    # Actualizar solo los campos enviados (no obligatorios)
    if datos:
        if 'nombre' in datos and datos['nombre']:
            taller.nombre_taller = datos['nombre']
        
        if 'email' in datos and datos['email']:
            taller.email = datos['email']
        
        if 'telefono' in datos and datos['telefono']:
            taller.telefono = datos['telefono']
        
        if 'direccion' in datos and datos['direccion']:
            taller.direccion = datos['direccion']
        
        if 'ciudad' in datos and datos['ciudad']:
            taller.ubicacion = datos['ciudad']
        
        if 'encargado' in datos and datos['encargado'] and usuario:
            usuario.nombre = datos['encargado']
        
        if 'especialidad' in datos and datos['especialidad']:
            # Si tienes campo especialidad en taller
            if hasattr(taller, 'especialidad'):
                taller.especialidad = datos['especialidad']
    
    db.commit()
    
    return {
        "message": "Perfil actualizado correctamente",
        "taller": {
            "id": taller.id,
            "nombre": taller.nombre_taller,
            "email": taller.email,
            "telefono": taller.telefono,
            "direccion": taller.direccion,
            "ciudad": taller.ubicacion,
            "encargado": usuario.nombre if usuario else ""
        }
    }