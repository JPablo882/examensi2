from collections import OrderedDict
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Usuario, Taller, Servicio

router = APIRouter(prefix="/api/dashboard/admin", tags=["Dashboard Admin"])


def normalizar_fecha(dt):
    if not dt:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


@router.get("/resumen")
def obtener_resumen_dashboard_admin(db: Session = Depends(get_db)):
    ahora = datetime.now(timezone.utc)
    inicio_mes = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    usuarios = db.query(Usuario).options(joinedload(Usuario.rol)).all()
    talleres = db.query(Taller).all()
    servicios = db.query(Servicio).options(joinedload(Servicio.pago)).all()

    usuarios_totales = len(usuarios)
    talleres_totales = len(talleres)
    solicitudes_activas = len([
        s for s in servicios
        if (s.estado or "").lower() in ["pendiente", "asignado", "en proceso", "en_proceso"]
    ])

    ingresos_mes = 0.0
    for s in servicios:
        if s.pago and s.pago.fecha:
            fecha_pago = normalizar_fecha(s.pago.fecha)
            if fecha_pago and fecha_pago >= inicio_mes:
                ingresos_mes += float(s.pago.monto)

    semanas = OrderedDict()
    for i in range(3, -1, -1):
        inicio_semana = (ahora - timedelta(days=ahora.weekday())) - timedelta(weeks=i)
        inicio_semana = inicio_semana.replace(hour=0, minute=0, second=0, microsecond=0)
        semanas[inicio_semana] = 0

    for u in usuarios:
        fecha_ref = normalizar_fecha(u.fecha_registro)
        if fecha_ref:
            for inicio_semana in semanas:
                fin_semana = inicio_semana + timedelta(days=7)
                if inicio_semana <= fecha_ref < fin_semana:
                    semanas[inicio_semana] += 1
                    break

    usuarios_labels = [f"Sem {i+1}" for i in range(len(semanas))]
    usuarios_data = list(semanas.values())

    talleres_activos = len([t for t in talleres if (t.estado or "").lower() == "activo"])
    talleres_pendientes = len([t for t in talleres if (t.estado or "").lower() == "pendiente"])
    talleres_inactivos = len([t for t in talleres if (t.estado or "").lower() == "inactivo"])

    talleres_labels = ["Activos", "Pendientes", "Inactivos"]
    talleres_data = [talleres_activos, talleres_pendientes, talleres_inactivos]

    dias = OrderedDict()
    for i in range(5, -1, -1):
        fecha = (ahora - timedelta(days=i)).date()
        dias[fecha] = 0

    for s in servicios:
        fecha_inicio = normalizar_fecha(s.inicio)
        if fecha_inicio and fecha_inicio.date() in dias:
            dias[fecha_inicio.date()] += 1

    solicitudes_labels = [d.strftime("%a") for d in dias.keys()]
    solicitudes_data = list(dias.values())

    meses = OrderedDict()
    for i in range(3, -1, -1):
        ref = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        year = ref.year
        month = ref.month - i
        while month <= 0:
            month += 12
            year -= 1
        key = datetime(year, month, 1, tzinfo=timezone.utc)
        meses[key] = 0.0

    for s in servicios:
        if s.pago and s.pago.fecha:
            fecha_pago = normalizar_fecha(s.pago.fecha)
            if fecha_pago:
                for inicio_m in meses:
                    fin_m = (inicio_m.replace(day=28) + timedelta(days=4)).replace(day=1)
                    if inicio_m <= fecha_pago < fin_m:
                        meses[inicio_m] += float(s.pago.monto)
                        break

    ingresos_labels = [m.strftime("%b") for m in meses.keys()]
    ingresos_data = [round(v, 2) for v in meses.values()]

    return {
        "cards": {
            "usuarios_totales": usuarios_totales,
            "talleres_registrados": talleres_totales,
            "solicitudes_activas": solicitudes_activas,
            "ingresos_mes": round(ingresos_mes, 2)
        },
        "charts": {
            "usuarios": {
                "labels": usuarios_labels,
                "data": usuarios_data
            },
            "talleres": {
                "labels": talleres_labels,
                "data": talleres_data
            },
            "solicitudes": {
                "labels": solicitudes_labels,
                "data": solicitudes_data
            },
            "ingresos": {
                "labels": ingresos_labels,
                "data": ingresos_data
            }
        }
    }