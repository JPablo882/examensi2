from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Servicio, Incidente

router = APIRouter(prefix="/api/admin/solicitudes", tags=["Admin Solicitudes"])


@router.get("/recientes")
def obtener_solicitudes_recientes(db: Session = Depends(get_db)):
    servicios = (
        db.query(Servicio)
        .options(
            joinedload(Servicio.taller),
            joinedload(Servicio.incidente).joinedload(Incidente.usuario)
        )
        .order_by(Servicio.inicio.desc().nullslast(), Servicio.id.desc())
        .limit(20)
        .all()
    )

    resultado = []

    for s in servicios:
        usuario_nombre = "Sin usuario"
        if s.incidente and s.incidente.usuario:
            usuario_nombre = s.incidente.usuario.nombre or "Sin usuario"

        taller_nombre = "Sin taller"
        if s.taller:
            taller_nombre = s.taller.nombre_taller or "Sin taller"

        servicio_nombre = "Sin servicio"
        if s.incidente:
            servicio_nombre = s.incidente.tipo_problema or "Sin servicio"

        resultado.append({
            "id": s.id,
            "servicio": servicio_nombre,
            "usuario": usuario_nombre,
            "taller": taller_nombre,
            "estado": s.estado or "",
            "fecha": s.inicio.isoformat() if s.inicio else ""
        })

    return resultado

# 🔥 NUEVO ENDPOINT: Detalle de una solicitud específica
@router.get("/{solicitud_id}")
def obtener_detalle_solicitud(solicitud_id: int, db: Session = Depends(get_db)):
    servicio = (
        db.query(Servicio)
        .options(
            joinedload(Servicio.taller),
            joinedload(Servicio.tecnico),
            joinedload(Servicio.incidente).joinedload(Incidente.usuario),
            joinedload(Servicio.incidente).joinedload(Incidente.vehiculo),
            joinedload(Servicio.pago)
        )
        .filter(Servicio.id == solicitud_id)
        .first()
    )
    
    if not servicio:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    
    incidente = servicio.incidente
    
    # Obtener datos del cliente
    usuario_nombre = "Sin cliente"
    if incidente and incidente.usuario:
        usuario_nombre = incidente.usuario.nombre
    
    # Obtener datos del técnico
    tecnico_nombre = "Sin asignar"
    if servicio.tecnico:
        tecnico_nombre = servicio.tecnico.nombre
    
    # Obtener datos del taller
    taller_nombre = "Sin taller"
    if servicio.taller:
        taller_nombre = servicio.taller.nombre_taller
    
    # Obtener datos del pago
    monto = 0
    if servicio.pago:
        monto = float(servicio.pago.monto)
    
    # Obtener datos del vehículo
    vehiculo_texto = "Sin vehículo"
    if incidente and incidente.vehiculo:
        v = incidente.vehiculo
        vehiculo_texto = f"{v.marca} {v.modelo} - {v.placa}"
    
    return {
        "id": servicio.id,
        "servicio": incidente.tipo_problema if incidente else "N/A",
        "usuario": usuario_nombre,
        "taller": taller_nombre,
        "tecnico": tecnico_nombre,
        "monto": monto,
        "estado": servicio.estado,
        "ubicacion": incidente.ubicacion if incidente else "",
        "descripcion": incidente.descripcion if incidente else "",
        "vehiculo": vehiculo_texto
    }