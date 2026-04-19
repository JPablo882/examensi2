from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Incidente, Evidencia
from app.schemas import EvidenciaCreate, EvidenciaResponse

router = APIRouter(prefix="/api/evidencias", tags=["Evidencias"])


@router.post("/", response_model=EvidenciaResponse, status_code=status.HTTP_201_CREATED)
def crear_evidencia(data: EvidenciaCreate, db: Session = Depends(get_db)):
    incidente = db.query(Incidente).filter(Incidente.id == data.incidente_id).first()
    if not incidente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El incidente no existe."
        )

    nueva_evidencia = Evidencia(
        incidente_id=data.incidente_id,
        tipo_archivo=data.tipo_archivo,
        url_archivo=data.url_archivo
    )

    db.add(nueva_evidencia)
    db.commit()
    db.refresh(nueva_evidencia)

    return nueva_evidencia


@router.get("/", response_model=list[EvidenciaResponse])
def listar_evidencias(db: Session = Depends(get_db)):
    return db.query(Evidencia).all()


@router.get("/{evidencia_id}", response_model=EvidenciaResponse)
def obtener_evidencia(evidencia_id: int, db: Session = Depends(get_db)):
    evidencia = db.query(Evidencia).filter(Evidencia.id == evidencia_id).first()
    if not evidencia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidencia no encontrada."
        )
    return evidencia


@router.put("/{evidencia_id}", response_model=EvidenciaResponse)
def actualizar_evidencia(evidencia_id: int, data: EvidenciaCreate, db: Session = Depends(get_db)):
    evidencia = db.query(Evidencia).filter(Evidencia.id == evidencia_id).first()
    if not evidencia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidencia no encontrada."
        )

    incidente = db.query(Incidente).filter(Incidente.id == data.incidente_id).first()
    if not incidente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El incidente no existe."
        )

    evidencia.incidente_id = data.incidente_id
    evidencia.tipo_archivo = data.tipo_archivo
    evidencia.url_archivo = data.url_archivo

    db.commit()
    db.refresh(evidencia)

    return evidencia


@router.delete("/{evidencia_id}")
def eliminar_evidencia(evidencia_id: int, db: Session = Depends(get_db)):
    evidencia = db.query(Evidencia).filter(Evidencia.id == evidencia_id).first()
    if not evidencia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidencia no encontrada."
        )

    db.delete(evidencia)
    db.commit()

    return {"message": "Evidencia eliminada correctamente."}