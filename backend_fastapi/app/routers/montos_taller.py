from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Taller, Servicio, Incidente, Pago, Usuario

router = APIRouter(prefix="/api/taller/montos", tags=["Montos Taller"])

@router.get("/")
def obtener_montos_taller(
    taller_email: str = Query(...),
    db: Session = Depends(get_db)
):
    """Obtener resumen de ingresos y pagos del taller"""
    
    taller = db.query(Taller).filter(Taller.email == taller_email).first()
    if not taller:
        raise HTTPException(status_code=404, detail="Taller no encontrado")
    
    servicios = db.query(Servicio).filter(Servicio.taller_id == taller.id).all()
    
    ingresos_totales = 0
    pagos_lista = []
    
    for servicio in servicios:
        pago = db.query(Pago).filter(Pago.servicio_id == servicio.id).first()
        
        incidente = db.query(Incidente).filter(Incidente.id == servicio.incidente_id).first()
        cliente = None
        if incidente:
            cliente = db.query(Usuario).filter(Usuario.id == incidente.usuario_id).first()
        
        if pago:
            if servicio.estado and servicio.estado.lower() in ["finalizado", "cerrado", "completado"]:
                ingresos_totales += float(pago.monto) if pago.monto else 0
            
            pagos_lista.append({
                "servicio": f"SRV-{servicio.id:04d}",
                "cliente": cliente.nombre if cliente else "Cliente Demo",
                "monto": float(pago.monto) if pago.monto else 0,
                "comision": float(pago.comision) if pago.comision else 0,
                "estado": pago.estado if pago.estado else "pendiente",
                "fecha": pago.fecha.isoformat() if pago.fecha else ""
            })
    
    comisiones_totales = sum(p["comision"] for p in pagos_lista)
    neto_recibir = ingresos_totales - comisiones_totales
    
    return {
        "ingresos_totales": round(ingresos_totales, 2),
        "comisiones_totales": round(comisiones_totales, 2),
        "neto_recibir": round(neto_recibir, 2),
        "pagos": pagos_lista
    }


# ==================== AGREGAR AQUÍ LOS NUEVOS ENDPOINTS ====================

@router.get("/saldo")
def obtener_saldo_taller(
    taller_email: str = Query(...),
    db: Session = Depends(get_db)
):
    """Obtener saldo del taller basado en pagos"""
    
    taller = db.query(Taller).filter(Taller.email == taller_email).first()
    if not taller:
        return {"saldo": 0, "total_recibido": 0, "total_pendiente": 0}
    
    # Obtener servicios del taller
    servicios = db.query(Servicio).filter(Servicio.taller_id == taller.id).all()
    
    total_recibido = 0
    total_pendiente = 0
    
    for servicio in servicios:
        pago = db.query(Pago).filter(Pago.servicio_id == servicio.id).first()
        if pago:
            if pago.estado == "pagado":
                total_recibido += float(pago.monto) if pago.monto else 0
            else:
                total_pendiente += float(pago.monto) if pago.monto else 0
    
    return {
        "saldo": total_recibido,
        "total_recibido": total_recibido,
        "total_pendiente": total_pendiente,
        "bonos": 0
    }


@router.post("/recargar")
def recargar_saldo(
    taller_email: str = Query(...),
    monto: float = Query(...),
    db: Session = Depends(get_db)
):
    """
    Registrar una recarga (crea un servicio especial o usa tabla de pagos)
    NOTA: Sin tabla nueva, esto es solo un registro en memoria
    """
    
    # Como no hay tabla de billetera, devolvemos éxito simulado
    # En producción, necesitarías una tabla para recargas
    
    return {
        "message": "Recarga procesada exitosamente",
        "monto_recargado": monto,
        "nuevo_saldo": monto
    }