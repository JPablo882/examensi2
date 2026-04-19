from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Servicio, Pago
from app.schemas import PagoCreate, PagoResponse

router = APIRouter(prefix="/api/pagos", tags=["Pagos"])


@router.post("/", response_model=PagoResponse, status_code=status.HTTP_201_CREATED)
def crear_pago(data: PagoCreate, db: Session = Depends(get_db)):
    servicio = db.query(Servicio).filter(Servicio.id == data.servicio_id).first()
    if not servicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El servicio no existe."
        )

    pago_existente = db.query(Pago).filter(Pago.servicio_id == data.servicio_id).first()
    if pago_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ese servicio ya tiene un pago registrado."
        )

    nuevo_pago = Pago(
        servicio_id=data.servicio_id,
        monto=data.monto,
        comision=data.comision,
        estado=data.estado
    )

    db.add(nuevo_pago)
    db.commit()
    db.refresh(nuevo_pago)

    return nuevo_pago


@router.get("/", response_model=list[PagoResponse])
def listar_pagos(db: Session = Depends(get_db)):
    return db.query(Pago).all()


@router.get("/{pago_id}", response_model=PagoResponse)
def obtener_pago(pago_id: int, db: Session = Depends(get_db)):
    pago = db.query(Pago).filter(Pago.id == pago_id).first()
    if not pago:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pago no encontrado."
        )
    return pago


@router.put("/{pago_id}", response_model=PagoResponse)
def actualizar_pago(pago_id: int, data: PagoCreate, db: Session = Depends(get_db)):
    pago = db.query(Pago).filter(Pago.id == pago_id).first()
    if not pago:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pago no encontrado."
        )

    servicio = db.query(Servicio).filter(Servicio.id == data.servicio_id).first()
    if not servicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El servicio no existe."
        )

    pago_existente = (
        db.query(Pago)
        .filter(Pago.servicio_id == data.servicio_id, Pago.id != pago_id)
        .first()
    )
    if pago_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ese servicio ya está asociado a otro pago."
        )

    pago.servicio_id = data.servicio_id
    pago.monto = data.monto
    pago.comision = data.comision
    pago.estado = data.estado

    db.commit()
    db.refresh(pago)

    return pago


@router.delete("/{pago_id}")
def eliminar_pago(pago_id: int, db: Session = Depends(get_db)):
    pago = db.query(Pago).filter(Pago.id == pago_id).first()
    if not pago:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pago no encontrado."
        )

    db.delete(pago)
    db.commit()

    return {"message": "Pago eliminado correctamente."}