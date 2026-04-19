from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Servicio, Historial
from app.schemas import HistorialCreate, HistorialResponse

router = APIRouter(prefix="/api/historiales", tags=["Historiales"])


@router.post("/", response_model=HistorialResponse, status_code=status.HTTP_201_CREATED)
def crear_historial(data: HistorialCreate, db: Session = Depends(get_db)):
    servicio = db.query(Servicio).filter(Servicio.id == data.servicio_id).first()
    if not servicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El servicio no existe."
        )

    nuevo_historial = Historial(
        servicio_id=data.servicio_id,
        estado=data.estado,
        descripcion=data.descripcion
    )

    db.add(nuevo_historial)
    db.commit()
    db.refresh(nuevo_historial)

    return nuevo_historial


@router.get("/", response_model=list[HistorialResponse])
def listar_historiales(db: Session = Depends(get_db)):
    return db.query(Historial).all()


@router.get("/{historial_id}", response_model=HistorialResponse)
def obtener_historial(historial_id: int, db: Session = Depends(get_db)):
    historial = db.query(Historial).filter(Historial.id == historial_id).first()
    if not historial:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Historial no encontrado."
        )
    return historial


@router.put("/{historial_id}", response_model=HistorialResponse)
def actualizar_historial(historial_id: int, data: HistorialCreate, db: Session = Depends(get_db)):
    historial = db.query(Historial).filter(Historial.id == historial_id).first()
    if not historial:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Historial no encontrado."
        )

    servicio = db.query(Servicio).filter(Servicio.id == data.servicio_id).first()
    if not servicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El servicio no existe."
        )

    historial.servicio_id = data.servicio_id
    historial.estado = data.estado
    historial.descripcion = data.descripcion

    db.commit()
    db.refresh(historial)

    return historial


@router.delete("/{historial_id}")
def eliminar_historial(historial_id: int, db: Session = Depends(get_db)):
    historial = db.query(Historial).filter(Historial.id == historial_id).first()
    if not historial:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Historial no encontrado."
        )

    db.delete(historial)
    db.commit()

    return {"message": "Historial eliminado correctamente."}