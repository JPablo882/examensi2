from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Usuario, Vehiculo, Incidente, Taller, Servicio
from app.schemas import IncidenteCreate, IncidenteResponse

router = APIRouter(prefix="/api/incidentes", tags=["Incidentes"])


@router.post("/", response_model=IncidenteResponse, status_code=status.HTTP_201_CREATED)
def crear_incidente(data: IncidenteCreate, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == data.usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario no existe."
        )

    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == data.vehiculo_id).first()
    if not vehiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El vehículo no existe."
        )

    if vehiculo.usuario_id != data.usuario_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El vehículo no pertenece al usuario indicado."
        )

    nuevo_incidente = Incidente(
        usuario_id=data.usuario_id,
        vehiculo_id=data.vehiculo_id,
        descripcion=data.descripcion,
        ubicacion=data.ubicacion,
        tipo_problema=data.tipo_problema,
        prioridad=data.prioridad,
        estado=data.estado
    )

    db.add(nuevo_incidente)
    db.commit()
    db.refresh(nuevo_incidente)

    return nuevo_incidente


@router.get("/", response_model=list[IncidenteResponse])
def listar_incidentes(db: Session = Depends(get_db)):
    incidentes = db.query(Incidente).all()
    return incidentes


@router.get("/disponibles")
def obtener_incidentes_disponibles(
    taller_email: str = Query(...),
    db: Session = Depends(get_db)
):
    taller = db.query(Taller).filter(Taller.email == taller_email).first()
    if not taller:
        return []

    servicios_existentes = (
        db.query(Servicio.incidente_id)
        .filter(Servicio.taller_id == taller.id)
        .all()
    )

    ids_ocupados = [s.incidente_id for s in servicios_existentes]

    query = (
        db.query(Incidente)
        .options(
            joinedload(Incidente.usuario),
            joinedload(Incidente.vehiculo)
        )
        .order_by(Incidente.id.desc())
    )

    if ids_ocupados:
      query = query.filter(~Incidente.id.in_(ids_ocupados))

    incidentes = query.all()

    return [
        {
            "id": i.id,
            "cliente": i.usuario.nombre if i.usuario else "Sin cliente",
            "servicio": i.tipo_problema,
            "ubicacion": i.ubicacion,
            "prioridad": (i.prioridad or "").title(),
            "fecha": i.fecha.isoformat() if i.fecha else "",
            "vehiculo": (
                f"{i.vehiculo.marca} {i.vehiculo.modelo} - {i.vehiculo.placa}"
                if i.vehiculo else "Sin vehículo"
            )
        }
        for i in incidentes
    ]


@router.get("/{incidente_id}", response_model=IncidenteResponse)
def obtener_incidente(incidente_id: int, db: Session = Depends(get_db)):
    incidente = db.query(Incidente).filter(Incidente.id == incidente_id).first()
    if not incidente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incidente no encontrado."
        )
    return incidente


@router.put("/{incidente_id}", response_model=IncidenteResponse)
def actualizar_incidente(incidente_id: int, data: IncidenteCreate, db: Session = Depends(get_db)):
    incidente = db.query(Incidente).filter(Incidente.id == incidente_id).first()
    if not incidente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incidente no encontrado."
        )

    usuario = db.query(Usuario).filter(Usuario.id == data.usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario no existe."
        )

    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == data.vehiculo_id).first()
    if not vehiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El vehículo no existe."
        )

    if vehiculo.usuario_id != data.usuario_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El vehículo no pertenece al usuario indicado."
        )

    incidente.usuario_id = data.usuario_id
    incidente.vehiculo_id = data.vehiculo_id
    incidente.descripcion = data.descripcion
    incidente.ubicacion = data.ubicacion
    incidente.tipo_problema = data.tipo_problema
    incidente.prioridad = data.prioridad
    incidente.estado = data.estado

    db.commit()
    db.refresh(incidente)

    return incidente


@router.delete("/{incidente_id}")
def eliminar_incidente(incidente_id: int, db: Session = Depends(get_db)):
    incidente = db.query(Incidente).filter(Incidente.id == incidente_id).first()
    if not incidente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incidente no encontrado."
        )

    db.delete(incidente)
    db.commit()

    return {"message": "Incidente eliminado correctamente."}