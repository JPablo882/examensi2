from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, EmailStr


# =========================
# AUTH
# =========================
class RegisterClienteRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    access_type: str


# 🔥 NUEVO: REGISTRO CLIENTE
class RegisterClienteRequest(BaseModel):
    nombre: str
    telefono: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    nombre: str
    email: EmailStr
    telefono: str | None
    rol: str

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    message: str
    user: UserResponse


class RegisterTallerRequest(BaseModel):
    nombreCompleto: str
    email: EmailStr
    telefono: str
    password: str
    confirmPassword: str
    aceptaTerminos: bool
    nombreTaller: str
    direccion: str
    ubicacion: str
    emailTaller: EmailStr


class RegisterTallerResponse(BaseModel):
    message: str
    user: UserResponse


# =========================
# ROLES
# =========================

class RolBase(BaseModel):
    nombre: str


class RolCreate(RolBase):
    pass


class RolResponse(RolBase):
    id: int

    model_config = {"from_attributes": True}


# =========================
# USUARIOS
# =========================

class UsuarioBase(BaseModel):
    nombre: str
    email: EmailStr
    telefono: str | None = None
    activo: bool = True
    rol_id: int


class UsuarioCreate(UsuarioBase):
    password: str


class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    email: EmailStr
    telefono: str | None
    activo: bool
    fecha_registro: datetime
    rol_id: int

    model_config = {"from_attributes": True}


# =========================
# TALLERES
# =========================

class TallerBase(BaseModel):
    usuario_id: int
    nombre_taller: str
    direccion: str
    ubicacion: str
    telefono: str
    email: EmailStr
    estado: str = "activo"


class TallerCreate(TallerBase):
    pass


class TallerResponse(TallerBase):
    id: int

    model_config = {"from_attributes": True}


# =========================
# VEHICULOS
# =========================

class VehiculoBase(BaseModel):
    usuario_id: int
    marca: str
    modelo: str
    placa: str


class VehiculoCreate(VehiculoBase):
    pass


class VehiculoResponse(VehiculoBase):
    id: int

    model_config = {"from_attributes": True}


# =========================
# INCIDENTES
# =========================

class IncidenteBase(BaseModel):
    usuario_id: int
    vehiculo_id: int
    descripcion: str
    ubicacion: str
    tipo_problema: str
    prioridad: str
    estado: str = "pendiente"


class IncidenteCreate(IncidenteBase):
    pass


class IncidenteResponse(IncidenteBase):
    id: int
    fecha: datetime

    model_config = {"from_attributes": True}


# =========================
# TECNICOS
# =========================

class TecnicoBase(BaseModel):
    taller_id: int
    nombre: str
    estado: str = "disponible"


class TecnicoCreate(TecnicoBase):
    pass


class TecnicoResponse(TecnicoBase):
    id: int

    model_config = {"from_attributes": True}


# =========================
# SERVICIOS
# =========================

class ServicioBase(BaseModel):
    taller_id: int
    tecnico_id: int | None = None
    incidente_id: int
    estado: str = "pendiente"
    tiempo_estimado: int | None = None
    inicio: datetime | None = None
    fin: datetime | None = None


class ServicioCreate(ServicioBase):
    pass


class ServicioResponse(ServicioBase):
    id: int

    model_config = {"from_attributes": True}


# =========================
# EVIDENCIAS
# =========================

class EvidenciaBase(BaseModel):
    incidente_id: int
    tipo_archivo: str
    url_archivo: str


class EvidenciaCreate(EvidenciaBase):
    pass


class EvidenciaResponse(EvidenciaBase):
    id: int

    model_config = {"from_attributes": True}


# =========================
# HISTORIALES
# =========================

class HistorialBase(BaseModel):
    servicio_id: int
    estado: str
    descripcion: str


class HistorialCreate(HistorialBase):
    pass


class HistorialResponse(HistorialBase):
    id: int
    fecha: datetime

    model_config = {"from_attributes": True}


# =========================
# PAGOS
# =========================

class PagoBase(BaseModel):
    servicio_id: int
    monto: Decimal
    comision: Decimal
    estado: str


class PagoCreate(PagoBase):
    pass


class PagoResponse(PagoBase):
    id: int
    fecha: datetime

    model_config = {"from_attributes": True}


# =========================
# CALIFICACIONES
# =========================

class CalificacionBase(BaseModel):
    servicio_id: int
    puntuacion: int
    comentarios: str | None = None


class CalificacionCreate(CalificacionBase):
    pass


class CalificacionResponse(CalificacionBase):
    id: int

    model_config = {"from_attributes": True}


# =========================
# METRICAS
# =========================

class MetricaBase(BaseModel):
    servicio_id: int
    tipo: str
    valor: Decimal


class MetricaCreate(MetricaBase):
    pass


class MetricaResponse(MetricaBase):
    id: int
    fecha: datetime

    model_config = {"from_attributes": True}
    
class PermisoBase(BaseModel):
    nombre: str


class PermisoCreate(PermisoBase):
    pass


class PermisoResponse(PermisoBase):
    id: int

    model_config = {"from_attributes": True}


class RolPermisoBase(BaseModel):
    rol_id: int
    permiso_id: int


class RolPermisoCreate(RolPermisoBase):
    pass


class RolPermisoResponse(RolPermisoBase):
    model_config = {"from_attributes": True}