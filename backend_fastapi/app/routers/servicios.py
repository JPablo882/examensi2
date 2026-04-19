from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Taller, Tecnico, Incidente, Servicio
from app.schemas import ServicioCreate, ServicioResponse

router = APIRouter(prefix="/api/servicios", tags=["Servicios"])


@router.post("/", response_model=ServicioResponse, status_code=status.HTTP_201_CREATED)
def crear_servicio(data: ServicioCreate, db: Session = Depends(get_db)):
    taller = db.query(Taller).filter(Taller.id == data.taller_id).first()
    if not taller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El taller no existe."
        )

    incidente = db.query(Incidente).filter(Incidente.id == data.incidente_id).first()
    if not incidente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El incidente no existe."
        )

    servicio_existente = db.query(Servicio).filter(Servicio.incidente_id == data.incidente_id).first()
    if servicio_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ese incidente ya tiene un servicio asignado."
        )

    if data.tecnico_id is not None:
        tecnico = db.query(Tecnico).filter(Tecnico.id == data.tecnico_id).first()
        if not tecnico:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El técnico no existe."
            )

        if tecnico.taller_id != data.taller_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El técnico no pertenece al taller indicado."
            )

    nuevo_servicio = Servicio(
        taller_id=data.taller_id,
        tecnico_id=data.tecnico_id,
        incidente_id=data.incidente_id,
        estado=data.estado,
        tiempo_estimado=data.tiempo_estimado,
        inicio=data.inicio,
        fin=data.fin
    )

    db.add(nuevo_servicio)
    db.commit()
    db.refresh(nuevo_servicio)

    return nuevo_servicio


@router.get("/", response_model=list[ServicioResponse])
def listar_servicios(db: Session = Depends(get_db)):
    return db.query(Servicio).all()


@router.get("/activas")
def obtener_servicios_activas(
    taller_email: str = Query(...),
    db: Session = Depends(get_db)
):
    taller = db.query(Taller).filter(Taller.email == taller_email).first()
    if not taller:
        return []

    servicios = (
        db.query(Servicio)
        .options(
            joinedload(Servicio.tecnico),
            joinedload(Servicio.incidente).joinedload(Incidente.usuario),
            joinedload(Servicio.incidente).joinedload(Incidente.vehiculo)
        )
        .filter(Servicio.taller_id == taller.id)
        .order_by(Servicio.id.desc())
        .all()
    )

    resultado = []

    for s in servicios:
        incidente = s.incidente
        usuario = incidente.usuario if incidente else None
        vehiculo = incidente.vehiculo if incidente else None
        tecnico = s.tecnico

        resultado.append({
            "codigo": f"SRV-{s.id:04d}",
            "servicio": incidente.tipo_problema if incidente else "Sin servicio",
            "cliente": usuario.nombre if usuario else "Sin cliente",
            "ubicacion": incidente.ubicacion if incidente else "Sin ubicación",
            "vehiculo": (
                f"{vehiculo.marca} {vehiculo.modelo} - {vehiculo.placa}"
                if vehiculo else "Sin vehículo"
            ),
            "tecnico": tecnico.nombre if tecnico else "",
            "telefonoTecnico": "",
            "estado": (s.estado or "").replace("_", " ").title(),
            "prioridad": (incidente.prioridad or "Media").title() if incidente else "Media",
            "fecha": s.inicio.isoformat() if s.inicio else ""
        })

    return resultado


@router.get("/{servicio_id}", response_model=ServicioResponse)
def obtener_servicio(servicio_id: int, db: Session = Depends(get_db)):
    servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()
    if not servicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no encontrado."
        )
    return servicio


@router.put("/{servicio_id}", response_model=ServicioResponse)
def actualizar_servicio(servicio_id: int, data: ServicioCreate, db: Session = Depends(get_db)):
    servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()
    if not servicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no encontrado."
        )

    taller = db.query(Taller).filter(Taller.id == data.taller_id).first()
    if not taller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El taller no existe."
        )

    incidente = db.query(Incidente).filter(Incidente.id == data.incidente_id).first()
    if not incidente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El incidente no existe."
        )

    servicio_existente = (
        db.query(Servicio)
        .filter(Servicio.incidente_id == data.incidente_id, Servicio.id != servicio_id)
        .first()
    )
    if servicio_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ese incidente ya está asignado a otro servicio."
        )

    if data.tecnico_id is not None:
        tecnico = db.query(Tecnico).filter(Tecnico.id == data.tecnico_id).first()
        if not tecnico:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El técnico no existe."
            )

        if tecnico.taller_id != data.taller_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El técnico no pertenece al taller indicado."
            )

    servicio.taller_id = data.taller_id
    servicio.tecnico_id = data.tecnico_id
    servicio.incidente_id = data.incidente_id
    servicio.estado = data.estado
    servicio.tiempo_estimado = data.tiempo_estimado
    servicio.inicio = data.inicio
    servicio.fin = data.fin

    db.commit()
    db.refresh(servicio)

    return servicio


@router.delete("/{servicio_id}")
def eliminar_servicio(servicio_id: int, db: Session = Depends(get_db)):
    servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()
    if not servicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no encontrado."
        )

    db.delete(servicio)
    db.commit()

    return {"message": "Servicio eliminado correctamente."}