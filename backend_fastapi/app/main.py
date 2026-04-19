from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app import models
from app.init_data import init_roles

from app.routers.auth import router as auth_router
from app.routers.vehiculos import router as vehiculos_router
from app.routers.incidentes import router as incidentes_router
from app.routers.tecnicos import router as tecnicos_router
from app.routers.servicios import router as servicios_router
from app.routers.evidencias import router as evidencias_router
from app.routers.historiales import router as historiales_router
from app.routers.pagos import router as pagos_router
from app.routers.calificaciones import router as calificaciones_router
from app.routers.metricas import router as metricas_router
from app.routers.dashboard_admin import router as dashboard_admin_router
from app.routers.admin_solicitudes import router as admin_solicitudes_router
from app.routers.admin_usuarios import router as admin_usuarios_router
from app.routers.dashboard_taller import router as dashboard_taller_router

app = FastAPI(title="EmergAuto FastAPI")

# 🔥 CREA TABLAS
Base.metadata.create_all(bind=engine)

# 🔥 CREA ROLES AUTOMÁTICOS
init_roles()

# 🔥 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 RUTAS
app.include_router(auth_router)
app.include_router(vehiculos_router)
app.include_router(incidentes_router)
app.include_router(tecnicos_router)
app.include_router(servicios_router)
app.include_router(evidencias_router)
app.include_router(historiales_router)
app.include_router(pagos_router)
app.include_router(calificaciones_router)
app.include_router(metricas_router)
app.include_router(dashboard_admin_router)
app.include_router(admin_solicitudes_router)
app.include_router(admin_usuarios_router)
app.include_router(dashboard_taller_router)

@app.get("/")
def root():
    return {"message": "Backend FastAPI funcionando correctamente"}