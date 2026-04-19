from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Usuario, Vehiculo
from app.schemas import VehiculoCreate, VehiculoResponse

router = APIRouter(prefix="/api/vehiculos", tags=["Vehiculos"])


@router.post("/", response_model=VehiculoResponse, status_code=status.HTTP_201_CREATED)
def crear_vehiculo(data: VehiculoCreate, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == data.usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario no existe."
        )

    placa_existente = db.query(Vehiculo).filter(Vehiculo.placa == data.placa).first()
    if placa_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un vehículo con esa placa."
        )

    nuevo_vehiculo = Vehiculo(
        usuario_id=data.usuario_id,
        marca=data.marca,
        modelo=data.modelo,
        placa=data.placa
    )

    db.add(nuevo_vehiculo)
    db.commit()
    db.refresh(nuevo_vehiculo)

    return nuevo_vehiculo


@router.get("/", response_model=list[VehiculoResponse])
def listar_vehiculos(db: Session = Depends(get_db)):
    vehiculos = db.query(Vehiculo).all()
    return vehiculos


@router.get("/{vehiculo_id}", response_model=VehiculoResponse)
def obtener_vehiculo(vehiculo_id: int, db: Session = Depends(get_db)):
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
    if not vehiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado."
        )
    return vehiculo


@router.put("/{vehiculo_id}", response_model=VehiculoResponse)
def actualizar_vehiculo(vehiculo_id: int, data: VehiculoCreate, db: Session = Depends(get_db)):
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
    if not vehiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado."
        )

    usuario = db.query(Usuario).filter(Usuario.id == data.usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario no existe."
        )

    placa_existente = (
        db.query(Vehiculo)
        .filter(Vehiculo.placa == data.placa, Vehiculo.id != vehiculo_id)
        .first()
    )
    if placa_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe otro vehículo con esa placa."
        )

    vehiculo.usuario_id = data.usuario_id
    vehiculo.marca = data.marca
    vehiculo.modelo = data.modelo
    vehiculo.placa = data.placa

    db.commit()
    db.refresh(vehiculo)

    return vehiculo


@router.delete("/{vehiculo_id}")
def eliminar_vehiculo(vehiculo_id: int, db: Session = Depends(get_db)):
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
    if not vehiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado."
        )

    db.delete(vehiculo)
    db.commit()

    return {"message": "Vehículo eliminado correctamente."}