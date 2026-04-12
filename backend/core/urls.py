from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    RolViewSet, PermisoViewSet, RolPermisoViewSet, UsuarioViewSet,
    TallerViewSet, TecnicoViewSet, VehiculoViewSet, IncidenteViewSet,
    EvidenciaViewSet, ServicioViewSet, HistorialViewSet,
    PagoViewSet, CalificacionViewSet, MetricaViewSet,
    LoginAPIView, RegisterTallerAPIView
)

router = DefaultRouter()
router.register(r'roles', RolViewSet)
router.register(r'permisos', PermisoViewSet)
router.register(r'rol-permisos', RolPermisoViewSet)
router.register(r'usuarios', UsuarioViewSet)
router.register(r'talleres', TallerViewSet)
router.register(r'tecnicos', TecnicoViewSet)
router.register(r'vehiculos', VehiculoViewSet)
router.register(r'incidentes', IncidenteViewSet)
router.register(r'evidencias', EvidenciaViewSet)
router.register(r'servicios', ServicioViewSet)
router.register(r'historiales', HistorialViewSet)
router.register(r'pagos', PagoViewSet)
router.register(r'calificaciones', CalificacionViewSet)
router.register(r'metricas', MetricaViewSet)

urlpatterns = [
    path('auth/login/', LoginAPIView.as_view(), name='auth-login'),
    path('auth/register-taller/', RegisterTallerAPIView.as_view(), name='auth-register-taller'),
] + router.urls