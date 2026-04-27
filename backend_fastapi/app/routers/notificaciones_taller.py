from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.models import Taller, Servicio, Incidente, Usuario, Historial

router = APIRouter(prefix="/api/taller/notificaciones", tags=["Notificaciones Taller"])

@router.get("/")
def obtener_notificaciones(
    taller_email: str = Query(...),
    db: Session = Depends(get_db)
):
    """Obtener notificaciones del taller"""
    
    taller = db.query(Taller).filter(Taller.email == taller_email).first()
    if not taller:
        return []
    
    notificaciones = []
    
    # 1. Notificaciones de nuevos servicios (últimos 7 días)
    servicios_nuevos = db.query(Servicio).filter(
        Servicio.taller_id == taller.id,
        Servicio.inicio >= datetime.now() - timedelta(days=7)
    ).order_by(Servicio.inicio.desc()).limit(5).all()
    
    for s in servicios_nuevos:
        incidente = db.query(Incidente).filter(Incidente.id == s.incidente_id).first()
        usuario = db.query(Usuario).filter(Usuario.id == incidente.usuario_id).first() if incidente else None
        
        notificaciones.append({
            "id": s.id,
            "titulo": "📋 Nuevo servicio asignado",
            "detalle": f"{incidente.tipo_problema if incidente else 'Servicio'} - {usuario.nombre if usuario else 'Cliente'}",
            "tiempo": calcular_tiempo_relativo(s.inicio),
            "fecha": s.inicio.isoformat() if s.inicio else "",
            "tipo": "servicio",
            "leida": False
        })
    
    # 2. Notificaciones de cambios de estado (últimos 7 días)
    historiales = db.query(Historial).filter(
        Historial.servicio_id.in_([s.id for s in servicios_nuevos])
    ).order_by(Historial.fecha.desc()).limit(5).all()
    
    for h in historiales:
        servicio = db.query(Servicio).filter(Servicio.id == h.servicio_id).first()
        if servicio and servicio.taller_id == taller.id:
            notificaciones.append({
                "id": h.id,
                "titulo": "🔄 Cambio de estado",
                "detalle": h.descripcion,
                "tiempo": calcular_tiempo_relativo(h.fecha),
                "fecha": h.fecha.isoformat(),
                "tipo": "estado",
                "leida": False
            })
    
    # 3. Incidentes pendientes
    incidentes_pendientes = db.query(Incidente).filter(
        Incidente.estado == "Pendiente"
    ).order_by(Incidente.fecha.desc()).limit(5).all()
    
    for inc in incidentes_pendientes:
        usuario = db.query(Usuario).filter(Usuario.id == inc.usuario_id).first()
        notificaciones.append({
            "id": inc.id,
            "titulo": "⚠️ Incidente reportado",
            "detalle": f"{inc.tipo_problema} - {usuario.nombre if usuario else 'Cliente'}",
            "tiempo": calcular_tiempo_relativo(inc.fecha),
            "fecha": inc.fecha.isoformat(),
            "tipo": "incidente",
            "leida": False
        })
    
    # Ordenar por fecha descendente y limitar a 10
    notificaciones.sort(key=lambda x: x["fecha"], reverse=True)
    
    return notificaciones[:10]

def calcular_tiempo_relativo(fecha):
    if not fecha:
        return "Recién"
    
    ahora = datetime.now()
    diff = ahora - fecha
    
    if diff.days > 7:
        return f"Hace {diff.days} días"
    elif diff.days > 0:
        return f"Hace {diff.days} día" if diff.days == 1 else f"Hace {diff.days} días"
    elif diff.seconds > 3600:
        horas = diff.seconds // 3600
        return f"Hace {horas} hora" if horas == 1 else f"Hace {horas} horas"
    elif diff.seconds > 60:
        minutos = diff.seconds // 60
        return f"Hace {minutos} min" if minutos == 1 else f"Hace {minutos} minutos"
    else:
        return "Hace unos segundos"