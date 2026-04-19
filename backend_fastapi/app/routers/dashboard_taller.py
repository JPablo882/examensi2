from collections import OrderedDict
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Servicio, Taller

router = APIRouter(prefix="/api/dashboard/taller", tags=["Dashboard Taller"])


def normalizar_fecha(dt):
    if not dt:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


@router.get("/resumen")
def obtener_resumen_dashboard_taller(
    taller_email: str = Query(...),
    db: Session = Depends(get_db)
):
    taller = db.query(Taller).filter(Taller.email == taller_email).first()
    if not taller:
        return {
            "cards": {
                "servicios_asignados": 0,
                "servicios_completados_mes": 0,
                "servicios_activos": 0,
                "ingresos_mes": 0
            },
            "charts": {
                "servicios": {"labels": [], "data": []},
                "completados": {"labels": [], "data": []},
                "activos": {"labels": [], "data": []},
                "ingresos": {"labels": [], "data": []}
            }
        }

    ahora = datetime.now(timezone.utc)
    inicio_mes = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    servicios = (
        db.query(Servicio)
        .options(joinedload(Servicio.pago))
        .filter(Servicio.taller_id == taller.id)
        .all()
    )

    servicios_asignados = len(servicios)
    servicios_completados_mes = len([
        s for s in servicios
        if (s.estado or "").lower() in ["completado", "finalizado", "cerrado"]
        and s.fin
        and normalizar_fecha(s.fin) >= inicio_mes
    ])
    servicios_activos = len([
        s for s in servicios
        if (s.estado or "").lower() in ["pendiente", "asignado", "en proceso", "en_proceso"]
    ])

    ingresos_mes = 0.0
    for s in servicios:
        if s.pago and s.pago.fecha:
            fecha_pago = normalizar_fecha(s.pago.fecha)
            if fecha_pago and fecha_pago >= inicio_mes:
                ingresos_mes += float(s.pago.monto)

    dias = OrderedDict()
    for i in range(6, -1, -1):
        fecha = (ahora - timedelta(days=i)).date()
        dias[fecha] = 0

    completados_dias = OrderedDict((d, 0) for d in dias.keys())
    activos_dias = OrderedDict((d, 0) for d in dias.keys())
    ingresos_dias = OrderedDict((d, 0.0) for d in dias.keys())

    for s in servicios:
        fecha_inicio = normalizar_fecha(s.inicio)
        if fecha_inicio and fecha_inicio.date() in dias:
            dias[fecha_inicio.date()] += 1

        fecha_fin = normalizar_fecha(s.fin)
        if fecha_fin and (s.estado or "").lower() in ["completado", "finalizado", "cerrado"]:
            if fecha_fin.date() in completados_dias:
                completados_dias[fecha_fin.date()] += 1

        if (s.estado or "").lower() in ["pendiente", "asignado", "en proceso", "en_proceso"]:
            fecha_ref = fecha_inicio.date() if fecha_inicio else ahora.date()
            if fecha_ref in activos_dias:
                activos_dias[fecha_ref] += 1

        if s.pago and s.pago.fecha:
            fecha_pago = normalizar_fecha(s.pago.fecha)
            if fecha_pago and fecha_pago.date() in ingresos_dias:
                ingresos_dias[fecha_pago.date()] += float(s.pago.monto)

    labels = [d.strftime("%a") for d in dias.keys()]

    return {
        "cards": {
            "servicios_asignados": servicios_asignados,
            "servicios_completados_mes": servicios_completados_mes,
            "servicios_activos": servicios_activos,
            "ingresos_mes": round(ingresos_mes, 2)
        },
        "charts": {
            "servicios": {
                "labels": labels,
                "data": list(dias.values())
            },
            "completados": {
                "labels": labels,
                "data": list(completados_dias.values())
            },
            "activos": {
                "labels": labels,
                "data": list(activos_dias.values())
            },
            "ingresos": {
                "labels": labels,
                "data": [round(v, 2) for v in ingresos_dias.values()]
            }
        }
    }