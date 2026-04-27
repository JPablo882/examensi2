from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Taller, Tecnico
from app.schemas import TecnicoCreate, TecnicoResponse

router = APIRouter(prefix="/api/tecnicos", tags=["Tecnicos"])


@router.post("/", response_model=TecnicoResponse, status_code=status.HTTP_201_CREATED)
def crear_tecnico(data: TecnicoCreate, db: Session = Depends(get_db)):
    taller = db.query(Taller).filter(Taller.id == data.taller_id).first()
    if not taller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El taller no existe."
        )

    nuevo_tecnico = Tecnico(
        taller_id=data.taller_id,
        nombre=data.nombre,
        estado=data.estado
    )

    db.add(nuevo_tecnico)
    db.commit()
    db.refresh(nuevo_tecnico)

    return nuevo_tecnico


@router.get("/", response_model=list[TecnicoResponse])
def listar_tecnicos(db: Session = Depends(get_db)):
    return db.query(Tecnico).all()


@router.get("/por-taller")
def obtener_tecnicos_por_taller(
    taller_id: int = Query(...),  # Cambiar de taller_email a taller_id
    db: Session = Depends(get_db)
):
    tecnicos = db.query(Tecnico).filter(Tecnico.taller_id == taller_id).all()
    
    return [
        {
            "id": t.id,
            "nombre": t.nombre,
            "estado": t.estado
        }
        for t in tecnicos
    ]


@router.get("/{tecnico_id}", response_model=TecnicoResponse)
def obtener_tecnico(tecnico_id: int, db: Session = Depends(get_db)):
    tecnico = db.query(Tecnico).filter(Tecnico.id == tecnico_id).first()
    if not tecnico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Técnico no encontrado."
        )
    return tecnico


@router.put("/{tecnico_id}", response_model=TecnicoResponse)
def actualizar_tecnico(tecnico_id: int, data: TecnicoCreate, db: Session = Depends(get_db)):
    tecnico = db.query(Tecnico).filter(Tecnico.id == tecnico_id).first()
    if not tecnico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Técnico no encontrado."
        )

    taller = db.query(Taller).filter(Taller.id == data.taller_id).first()
    if not taller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El taller no existe."
        )

    tecnico.taller_id = data.taller_id
    tecnico.nombre = data.nombre
    tecnico.estado = data.estado

    db.commit()
    db.refresh(tecnico)

    return tecnico

@router.put("/{tecnico_id}/estado")
def cambiar_estado_tecnico(
    tecnico_id: int,
    estado: str = Query(...),
    db: Session = Depends(get_db)
):
    tecnico = db.query(Tecnico).filter(Tecnico.id == tecnico_id).first()
    if not tecnico:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")
    
    # Aceptar cualquier estado (disponible, ocupado, activo, inactivo)
    tecnico.estado = estado
    db.commit()
    return {"id": tecnico.id, "estado": tecnico.estado}

@router.delete("/{tecnico_id}")
def eliminar_tecnico(tecnico_id: int, db: Session = Depends(get_db)):
    tecnico = db.query(Tecnico).filter(Tecnico.id == tecnico_id).first()
    if not tecnico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Técnico no encontrado."
        )

    db.delete(tecnico)
    db.commit()

    return {"message": "Técnico eliminado correctamente."}