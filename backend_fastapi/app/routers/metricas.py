from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Servicio, Metrica
from app.schemas import MetricaCreate, MetricaResponse

router = APIRouter(prefix="/api/metricas", tags=["Metricas"])


@router.post("/", response_model=MetricaResponse, status_code=status.HTTP_201_CREATED)
def crear_metrica(data: MetricaCreate, db: Session = Depends(get_db)):
    servicio = db.query(Servicio).filter(Servicio.id == data.servicio_id).first()
    if not servicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El servicio no existe."
        )

    nueva_metrica = Metrica(
        servicio_id=data.servicio_id,
        tipo=data.tipo,
        valor=data.valor
    )

    db.add(nueva_metrica)
    db.commit()
    db.refresh(nueva_metrica)

    return nueva_metrica


@router.get("/", response_model=list[MetricaResponse])
def listar_metricas(db: Session = Depends(get_db)):
    return db.query(Metrica).all()


@router.get("/{metrica_id}", response_model=MetricaResponse)
def obtener_metrica(metrica_id: int, db: Session = Depends(get_db)):
    metrica = db.query(Metrica).filter(Metrica.id == metrica_id).first()
    if not metrica:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Métrica no encontrada."
        )
    return metrica


@router.put("/{metrica_id}", response_model=MetricaResponse)
def actualizar_metrica(metrica_id: int, data: MetricaCreate, db: Session = Depends(get_db)):
    metrica = db.query(Metrica).filter(Metrica.id == metrica_id).first()
    if not metrica:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Métrica no encontrada."
        )

    servicio = db.query(Servicio).filter(Servicio.id == data.servicio_id).first()
    if not servicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El servicio no existe."
        )

    metrica.servicio_id = data.servicio_id
    metrica.tipo = data.tipo
    metrica.valor = data.valor

    db.commit()
    db.refresh(metrica)

    return metrica


@router.delete("/{metrica_id}")
def eliminar_metrica(metrica_id: int, db: Session = Depends(get_db)):
    metrica = db.query(Metrica).filter(Metrica.id == metrica_id).first()
    if not metrica:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Métrica no encontrada."
        )

    db.delete(metrica)
    db.commit()

    return {"message": "Métrica eliminada correctamente."}