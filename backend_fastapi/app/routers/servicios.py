from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel

from app.database import get_db
from app.models import Taller, Tecnico, Incidente, Servicio, Historial, Pago ,Usuario,Vehiculo
from app.schemas import ServicioCreate, ServicioResponse

router = APIRouter(prefix="/api/servicios", tags=["Servicios"])

# =========================
# MODELOS PARA PETICIONES
# =========================

class ActualizarEstadoRequest(BaseModel):
    """Modelo para actualizar el estado de un servicio"""
    nuevo_estado: str

class AsignarTecnicoRequest(BaseModel):
    """Modelo para asignar técnico a un servicio"""
    tecnico_id: int

# =========================
# ENDPOINTS
# =========================

@router.post("/", response_model=ServicioResponse, status_code=status.HTTP_201_CREATED)
def crear_servicio(data: ServicioCreate, db: Session = Depends(get_db)):
    """Crear un nuevo servicio a partir de un incidente"""
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

    # Registrar en historial
    nuevo_historial = Historial(
        servicio_id=nuevo_servicio.id,
        estado=nuevo_servicio.estado,
        descripcion=f"Servicio creado a partir del incidente #{incidente.id}"
    )
    db.add(nuevo_historial)
    db.commit()

    return nuevo_servicio


@router.get("/", response_model=list[ServicioResponse])
def listar_servicios(db: Session = Depends(get_db)):
    """Listar todos los servicios"""
    return db.query(Servicio).all()


@router.get("/activas")
def obtener_servicios_activas(
    taller_email: str = Query(...),
    db: Session = Depends(get_db)
):
    # Buscar el taller por email
    taller = db.query(Taller).filter(Taller.email == taller_email).first()
    if not taller:
        return []
    
    print(f"🔍 Taller: {taller.nombre_taller} (ID: {taller.id})")
    
    # Solo servicios de este taller
    servicios = db.query(Servicio).filter(
        Servicio.taller_id == taller.id
    ).all()
    
    print(f"📊 Servicios en BD para este taller: {len(servicios)}")
    
    resultado = []
    
    for s in servicios:
        incidente = s.incidente
        if incidente:
            usuario = incidente.usuario
            tecnico = s.tecnico
            
            # ✅ OBTENER VEHÍCULO - CON TUS CAMPOS REALES
            vehiculo_texto = "Sin vehículo"
            if incidente.vehiculo_id:
                vehiculo = db.query(Vehiculo).filter(Vehiculo.id == incidente.vehiculo_id).first()
                if vehiculo:
                    # Solo los campos que tienes en tu tabla: marca, modelo, placa
                    vehiculo_texto = f"{vehiculo.marca} {vehiculo.modelo} ({vehiculo.placa})"
            
            print(f"  - Servicio ID: {s.id}, Vehículo: {vehiculo_texto}")
            
            resultado.append({
                "id": s.id,
                "codigo": f"SRV-{s.id:04d}",
                "servicio": incidente.tipo_problema,
                "cliente": usuario.nombre if usuario else "Cliente",
                "ubicacion": incidente.ubicacion,
                "vehiculo": vehiculo_texto,  # ✅ AHORA SÍ MUESTRA EL VEHÍCULO
                "tecnico": tecnico.nombre if tecnico else "Sin asignar",
                "telefonoTecnico": "",
                "estado": s.estado.title(),
                "prioridad": incidente.prioridad.title(),
                "fecha": s.inicio.isoformat() if s.inicio else ""
            })
    
    print(f"✅ Total devuelto: {len(resultado)}")
    return resultado


@router.get("/{servicio_id}")
def obtener_servicio(servicio_id: int, db: Session = Depends(get_db)):
    """Obtener un servicio por ID incluyendo vehículo"""
    
    servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()
    
    if not servicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no encontrado."
        )
    
    incidente = servicio.incidente
    
    # ✅ OBTENER VEHÍCULO
    vehiculo_info = None
    if incidente and incidente.vehiculo_id:
        vehiculo = db.query(Vehiculo).filter(Vehiculo.id == incidente.vehiculo_id).first()
        if vehiculo:
            vehiculo_info = {
                "id": vehiculo.id,
                "marca": vehiculo.marca,
                "modelo": vehiculo.modelo,
                "placa": vehiculo.placa
            }
    
    return {
        "id": servicio.id,
        "taller_id": servicio.taller_id,
        "tecnico_id": servicio.tecnico_id,
        "incidente_id": servicio.incidente_id,
        "estado": servicio.estado,
        "tiempo_estimado": servicio.tiempo_estimado,
        "inicio": servicio.inicio.isoformat() if servicio.inicio else "",
        "fin": servicio.fin.isoformat() if servicio.fin else "",
        "incidente": {
            "id": incidente.id,
            "tipo_problema": incidente.tipo_problema,
            "descripcion": incidente.descripcion,
            "ubicacion": incidente.ubicacion,
            "prioridad": incidente.prioridad,
            "usuario": {
                "id": incidente.usuario.id,
                "nombre": incidente.usuario.nombre
            } if incidente.usuario else None
        } if incidente else None,
        "tecnico": {
            "id": servicio.tecnico.id,
            "nombre": servicio.tecnico.nombre
        } if servicio.tecnico else None,
        "vehiculo": vehiculo_info  # ✅ VEHÍCULO INCLUIDO
    }

@router.get("/historial")
def obtener_historial_taller(
    taller_email: str = Query(...),
    db: Session = Depends(get_db)
):
    """Obtener historial de servicios completados de un taller"""
    taller = db.query(Taller).filter(Taller.email == taller_email).first()
    if not taller:
        return []

    servicios = (
        db.query(Servicio)
        .options(
            joinedload(Servicio.pago),
            joinedload(Servicio.incidente).joinedload(Incidente.usuario)
        )
        .filter(
            Servicio.taller_id == taller.id,
            Servicio.estado.in_(["completado", "finalizado", "cerrado"])
        )
        .order_by(Servicio.fin.desc(), Servicio.id.desc())
        .all()
    )

    resultado = []

    for s in servicios:
        incidente = s.incidente
        usuario = incidente.usuario if incidente else None
        pago = s.pago

        resultado.append({
            "id": s.id,
            "servicio": incidente.tipo_problema if incidente else "Sin servicio",
            "cliente": usuario.nombre if usuario else "Sin cliente",
            "estado": (s.estado or "").replace("_", " ").title(),
            "monto": float(pago.monto) if pago and pago.monto is not None else 0,
            "fecha": s.fin.isoformat() if s.fin else (s.inicio.isoformat() if s.inicio else "")
        })

    return resultado


@router.put("/{servicio_id}/asignar-tecnico")
def asignar_tecnico_a_servicio(
    servicio_id: int,
    tecnico_id: int,
    db: Session = Depends(get_db)
):
    """Asignar un técnico a un servicio (query params)"""
    servicio = (
        db.query(Servicio)
        .options(
            joinedload(Servicio.tecnico),
            joinedload(Servicio.incidente)
        )
        .filter(Servicio.id == servicio_id)
        .first()
    )

    if not servicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no encontrado."
        )

    tecnico = db.query(Tecnico).filter(Tecnico.id == tecnico_id).first()
    if not tecnico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Técnico no encontrado."
        )

    if tecnico.taller_id != servicio.taller_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El técnico no pertenece al mismo taller del servicio."
        )

    estado_anterior = servicio.estado
    servicio.tecnico_id = tecnico.id
    servicio.estado = "asignado"

    if not servicio.inicio:
        servicio.inicio = datetime.now(timezone.utc)

    nuevo_historial = Historial(
        servicio_id=servicio.id,
        estado="asignado",
        descripcion=f"Técnico asignado: {tecnico.nombre} (estado anterior: {estado_anterior})"
    )

    db.add(nuevo_historial)
    db.commit()
    db.refresh(servicio)

    return {
        "message": "Técnico asignado correctamente.",
        "servicio_id": servicio.id,
        "tecnico_id": tecnico.id,
        "tecnico_nombre": tecnico.nombre,
        "estado": servicio.estado
    }


@router.put("/{servicio_id}/asignar-tecnico-body")
def asignar_tecnico_con_body(
    servicio_id: int,
    request: AsignarTecnicoRequest,
    db: Session = Depends(get_db)
):
    """Asignar un técnico a un servicio (con body) - Alternativa más RESTful"""
    return asignar_tecnico_a_servicio(servicio_id, request.tecnico_id, db)


@router.get("/{servicio_id}", response_model=ServicioResponse)
def obtener_servicio(servicio_id: int, db: Session = Depends(get_db)):
    """Obtener un servicio por ID"""
    servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()
    if not servicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no encontrado."
        )
    return servicio


@router.put("/{servicio_id}/actualizar-estado")
def actualizar_estado_servicio(
    servicio_id: int, 
    request: ActualizarEstadoRequest,
    db: Session = Depends(get_db)
):
    
    """Actualizar el estado de un servicio"""
    
    servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()
    
    if not servicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no encontrado"
        )
    
    # 🔥 ESTADOS VÁLIDOS - Agregar "Finalizado"
    estados_validos = ["pendiente", "aceptada", "asignado", "en_proceso", "finalizado", "cerrado", "completado", "Activo", "Pendiente", "Aceptada", "Asignado", "Finalizado"]
    
    if request.nuevo_estado.lower() not in [e.lower() for e in estados_validos]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado inválido. Estados válidos: pendiente, aceptada, asignado, en_proceso, finalizado, cerrado"
        )
    
    # Guardar estado anterior
    estado_anterior = servicio.estado
    
    # Actualizar el estado
    servicio.estado = request.nuevo_estado
    
    # Si el servicio se finaliza o cierra, registrar fecha de fin
    if request.nuevo_estado in ["finalizado", "cerrado", "completado"] and not servicio.fin:
        servicio.fin = datetime.now(timezone.utc)
    
    
    
     # 🔥 NUEVO: Si el servicio se finaliza, actualizar el estado del pago a "pagado"
    if request.nuevo_estado.lower() in ["finalizado", "cerrado", "completado"]:
        pago = db.query(Pago).filter(Pago.servicio_id == servicio_id).first()
        if pago:
            pago.estado = "pagado"
            if not pago.fecha:
                pago.fecha = datetime.now(timezone.utc)
    
    # Registrar en el historial
    nuevo_historial = Historial(
        servicio_id=servicio.id,
        estado=request.nuevo_estado,
        descripcion=f"Estado actualizado de '{estado_anterior}' a '{request.nuevo_estado}'"
    )
    
    db.add(nuevo_historial)
    db.commit()
    db.refresh(servicio)
    
    return {
        "message": f"Estado actualizado de '{estado_anterior}' a '{servicio.estado}'",
        "servicio_id": servicio.id,
        "estado_anterior": estado_anterior,
        "nuevo_estado": servicio.estado,
        "fecha_actualizacion": datetime.now(timezone.utc).isoformat()
    }


# Endpoint alternativo usando query params (para compatibilidad)
@router.put("/{servicio_id}/actualizar-estado-query")
def actualizar_estado_query(
    servicio_id: int,
    nuevo_estado: str = Query(..., description="Nuevo estado del servicio"),
    db: Session = Depends(get_db)
):
    """Actualizar estado usando query params (para compatibilidad con versiones anteriores)"""
    servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()
    
    if not servicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no encontrado"
        )
    
    servicio.estado = nuevo_estado
    db.commit()
    db.refresh(servicio)
    
    return servicio


@router.delete("/{servicio_id}")
def eliminar_servicio(servicio_id: int, db: Session = Depends(get_db)):
    """Eliminar un servicio"""
    servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()
    if not servicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no encontrado."
        )

    db.delete(servicio)
    db.commit()

    return {"message": "Servicio eliminado correctamente."}

@router.put("/{incidente_id}/aceptar")
def aceptar_solicitud(
    incidente_id: int,
    taller_email: str = Query(...),
    db: Session = Depends(get_db)
):
    """Aceptar una solicitud (cambiar estado de Pendiente a Aceptada)"""
    
    incidente = db.query(Incidente).filter(Incidente.id == incidente_id).first()
    
    if not incidente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incidente no encontrado"
        )
    
    if incidente.estado != "Pendiente":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El incidente está {incidente.estado}, no se puede aceptar"
        )
    
    incidente.estado = "Aceptada"
    
    taller = db.query(Taller).filter(Taller.email == taller_email).first()
    
    if taller:
        servicio_existente = db.query(Servicio).filter(Servicio.incidente_id == incidente_id).first()
        
        if not servicio_existente:
            nuevo_servicio = Servicio(
                taller_id=taller.id,
                incidente_id=incidente_id,
                estado="aceptada",
                inicio=datetime.now(timezone.utc)
            )
            db.add(nuevo_servicio)
            
            nuevo_historial = Historial(
                servicio_id=nuevo_servicio.id,
                estado="aceptada",
                descripcion=f"Solicitud aceptada por taller {taller.nombre_taller}"
            )
            db.add(nuevo_historial)
    
    db.commit()
    
    return {
        "message": "Solicitud aceptada correctamente",
        "incidente_id": incidente.id,
        "nuevo_estado": incidente.estado
    }
    
    
@router.put("/{servicio_id}/aceptar-servicio")
def aceptar_servicio(
    servicio_id: int,
    taller_email: str = Query(...),
    db: Session = Depends(get_db)
):
    """Aceptar un servicio (cambiar estado de Pendiente a Aceptada)"""
    
    # Buscar el servicio
    servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()
    
    if not servicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no encontrado"
        )
    
    # Verificar que esté pendiente
    if servicio.estado != "Pendiente":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El servicio está {servicio.estado}, no se puede aceptar"
        )
    
    # Cambiar estado
    servicio.estado = "aceptada"
    
    # Registrar en historial
    nuevo_historial = Historial(
        servicio_id=servicio.id,
        estado="aceptada",
        descripcion=f"Servicio aceptado por taller"
    )
    db.add(nuevo_historial)
    
    db.commit()
    
    return {
        "message": "Servicio aceptado correctamente",
        "servicio_id": servicio.id,
        "nuevo_estado": servicio.estado
    }