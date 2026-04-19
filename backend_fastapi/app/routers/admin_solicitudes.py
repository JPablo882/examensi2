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