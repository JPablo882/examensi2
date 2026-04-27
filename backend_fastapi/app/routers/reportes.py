from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import Pago, Servicio, Taller, Incidente

router = APIRouter(prefix="/api/reportes", tags=["Reportes"])

# ==================== ENDPOINT DE PAGOS (ya lo tienes) ====================
@router.get("/pagos")
def obtener_reportes_pagos(
    taller_email: str = Query(None),
    db: Session = Depends(get_db)
):
    """Obtener todos los pagos para reportes"""
    
    query = db.query(Pago).join(Servicio, Servicio.id == Pago.servicio_id)
    
    if taller_email:
        taller = db.query(Taller).filter(Taller.email == taller_email).first()
        if taller:
            query = query.filter(Servicio.taller_id == taller.id)
    
    pagos = query.order_by(Pago.fecha.desc()).all()
    
    return [
        {
            "id": p.id,
            "servicio_id": p.servicio_id,
            "monto": float(p.monto),
            "comision": float(p.comision),
            "estado": p.estado,
            "fecha": p.fecha.isoformat() if p.fecha else ""
        }
        for p in pagos
    ]


# ==================== ✅ ENDPOINT DE SERVICIOS (AGREGAR ESTE) ====================
@router.get("/servicios")
def obtener_reportes_servicios(
    taller_email: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Obtener todos los servicios para reportes
    Campos: id, taller_id, incidente_id, estado, tiempo_estimado, inicio, fin
    """
    
    query = db.query(Servicio)
    
    # Filtrar por taller si se envía email
    if taller_email:
        taller = db.query(Taller).filter(Taller.email == taller_email).first()
        if taller:
            query = query.filter(Servicio.taller_id == taller.id)
    
    # Filtrar por estado si se envía
    if estado:
        query = query.filter(Servicio.estado == estado)
    
    # Ordenar por fecha de inicio descendente
    servicios = query.order_by(Servicio.inicio.desc()).all()
    
    return [
        {
            "id": s.id,
            "taller_id": s.taller_id,
            "incidente_id": s.incidente_id,
            "estado": s.estado,
            "tiempo_estimado": s.tiempo_estimado,
            "inicio": s.inicio.isoformat() if s.inicio else "",
            "fin": s.fin.isoformat() if s.fin else ""
        }
        for s in servicios
    ]


# ==================== ✅ ENDPOINT PARA UN SOLO SERVICIO (detalle) ====================
@router.get("/servicios/{servicio_id}")
def obtener_detalle_servicio(
    servicio_id: int,
    db: Session = Depends(get_db)
):
    """Obtener detalle completo de un servicio específico"""
    
    servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()
    
    if not servicio:
        return {"error": "Servicio no encontrado"}
    
    return {
        "id": servicio.id,
        "taller_id": servicio.taller_id,
        "taller_nombre": servicio.taller.nombre_taller if servicio.taller else None,
        "incidente_id": servicio.incidente_id,
        "incidente_tipo": servicio.incidente.tipo if servicio.incidente else None,
        "estado": servicio.estado,
        "tiempo_estimado": servicio.tiempo_estimado,
        "inicio": servicio.inicio.isoformat() if servicio.inicio else "",
        "fin": servicio.fin.isoformat() if servicio.fin else "",
        "duracion_minutos": (servicio.fin - servicio.inicio).total_seconds() / 60 if servicio.fin and servicio.inicio else None
    }


# ==================== ✅ ENDPOINT DE ESTADÍSTICAS DE SERVICIOS ====================
@router.get("/servicios/estadisticas")
def obtener_estadisticas_servicios(
    taller_email: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Obtener estadísticas de servicios (totales, por estado, etc.)"""
    
    query = db.query(Servicio)
    
    if taller_email:
        taller = db.query(Taller).filter(Taller.email == taller_email).first()
        if taller:
            query = query.filter(Servicio.taller_id == taller.id)
    
    servicios = query.all()
    
    # Contar por estado
    estados = {}
    for s in servicios:
        estado = s.estado
        estados[estado] = estados.get(estado, 0) + 1
    
    # Calcular tiempo total
    tiempo_total = sum(s.tiempo_estimado or 0 for s in servicios)
    
    return {
        "total_servicios": len(servicios),
        "tiempo_total_estimado": tiempo_total,
        "servicios_por_estado": estados,
        "promedio_tiempo": tiempo_total / len(servicios) if servicios else 0
    }