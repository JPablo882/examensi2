from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Servicio, Calificacion
from app.schemas import CalificacionCreate, CalificacionResponse

router = APIRouter(prefix="/api/calificaciones", tags=["Calificaciones"])


@router.post("/", response_model=CalificacionResponse, status_code=status.HTTP_201_CREATED)
def crear_calificacion(data: CalificacionCreate, db: Session = Depends(get_db)):
    servicio = db.query(Servicio).filter(Servicio.id == data.servicio_id).first()
    if not servicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El servicio no existe."
        )

    calificacion_existente = (
        db.query(Calificacion)
        .filter(Calificacion.servicio_id == data.servicio_id)
        .first()
    )
    if calificacion_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ese servicio ya tiene una calificación registrada."
        )

    nueva_calificacion = Calificacion(
        servicio_id=data.servicio_id,
        puntuacion=data.puntuacion,
        comentarios=data.comentarios
    )

    db.add(nueva_calificacion)
    db.commit()
    db.refresh(nueva_calificacion)

    return nueva_calificacion


@router.get("/", response_model=list[CalificacionResponse])
def listar_calificaciones(db: Session = Depends(get_db)):
    return db.query(Calificacion).all()


@router.get("/{calificacion_id}", response_model=CalificacionResponse)
def obtener_calificacion(calificacion_id: int, db: Session = Depends(get_db)):
    calificacion = db.query(Calificacion).filter(Calificacion.id == calificacion_id).first()
    if not calificacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calificación no encontrada."
        )
    return calificacion


@router.put("/{calificacion_id}", response_model=CalificacionResponse)
def actualizar_calificacion(calificacion_id: int, data: CalificacionCreate, db: Session = Depends(get_db)):
    calificacion = db.query(Calificacion).filter(Calificacion.id == calificacion_id).first()
    if not calificacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calificación no encontrada."
        )

    servicio = db.query(Servicio).filter(Servicio.id == data.servicio_id).first()
    if not servicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El servicio no existe."
        )

    calificacion_existente = (
        db.query(Calificacion)
        .filter(Calificacion.servicio_id == data.servicio_id, Calificacion.id != calificacion_id)
        .first()
    )
    if calificacion_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ese servicio ya está asociado a otra calificación."
        )

    calificacion.servicio_id = data.servicio_id
    calificacion.puntuacion = data.puntuacion
    calificacion.comentarios = data.comentarios

    db.commit()
    db.refresh(calificacion)

    return calificacion


@router.delete("/{calificacion_id}")
def eliminar_calificacion(calificacion_id: int, db: Session = Depends(get_db)):
    calificacion = db.query(Calificacion).filter(Calificacion.id == calificacion_id).first()
    if not calificacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calificación no encontrada."
        )

    db.delete(calificacion)
    db.commit()

    return {"message": "Calificación eliminada correctamente."}