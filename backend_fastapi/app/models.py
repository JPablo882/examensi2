from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Rol(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)

    usuarios = relationship("Usuario", back_populates="rol")
    roles_permiso = relationship("RolPermiso", back_populates="rol", cascade="all, delete-orphan")
    
class Permiso(Base):
    __tablename__ = "permisos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)

    permisos_roles = relationship("RolPermiso", back_populates="permiso", cascade="all, delete-orphan")


class RolPermiso(Base):
    __tablename__ = "rol_permiso"

    rol_id = Column(Integer, ForeignKey("roles.id"), primary_key=True, nullable=False)
    permiso_id = Column(Integer, ForeignKey("permisos.id"), primary_key=True, nullable=False)

    rol = relationship("Rol", back_populates="roles_permiso")
    permiso = relationship("Permiso", back_populates="permisos_roles")

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    email = Column(String(254), unique=True, nullable=False, index=True)
    telefono = Column(String(20), nullable=True)
    password_hash = Column(String(255), nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_registro = Column(DateTime, server_default=func.now(), nullable=False)

    rol_id = Column(Integer, ForeignKey("roles.id"), nullable=False)

    rol = relationship("Rol", back_populates="usuarios")
    taller = relationship("Taller", back_populates="usuario", uselist=False)
    vehiculos = relationship("Vehiculo", back_populates="usuario", cascade="all, delete-orphan")
    incidentes = relationship("Incidente", back_populates="usuario", cascade="all, delete-orphan")


class Taller(Base):
    __tablename__ = "talleres"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True, nullable=False)
    nombre_taller = Column(String(150), nullable=False)
    direccion = Column(String(255), nullable=False)
    ubicacion = Column(String(255), nullable=False)
    telefono = Column(String(20), nullable=False)
    email = Column(String(254), nullable=False)
    estado = Column(String(30), default="activo", nullable=False)

    usuario = relationship("Usuario", back_populates="taller")
    tecnicos = relationship("Tecnico", back_populates="taller", cascade="all, delete-orphan")
    servicios = relationship("Servicio", back_populates="taller", cascade="all, delete-orphan")


class Vehiculo(Base):
    __tablename__ = "vehiculos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    marca = Column(String(100), nullable=False)
    modelo = Column(String(100), nullable=False)
    placa = Column(String(20), unique=True, nullable=False)

    usuario = relationship("Usuario", back_populates="vehiculos")
    incidentes = relationship("Incidente", back_populates="vehiculo", cascade="all, delete-orphan")


class Incidente(Base):
    __tablename__ = "incidentes"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    vehiculo_id = Column(Integer, ForeignKey("vehiculos.id"), nullable=False)

    descripcion = Column(Text, nullable=False)
    ubicacion = Column(String(255), nullable=False)
    tipo_problema = Column(String(100), nullable=False)
    prioridad = Column(String(30), nullable=False)
    estado = Column(String(30), nullable=False, default="pendiente")
    fecha = Column(DateTime, server_default=func.now(), nullable=False)

    usuario = relationship("Usuario", back_populates="incidentes")
    vehiculo = relationship("Vehiculo", back_populates="incidentes")
    servicio = relationship("Servicio", back_populates="incidente", uselist=False)
    evidencias = relationship("Evidencia", back_populates="incidente", cascade="all, delete-orphan")


class Tecnico(Base):
    __tablename__ = "tecnicos"

    id = Column(Integer, primary_key=True, index=True)
    taller_id = Column(Integer, ForeignKey("talleres.id"), nullable=False)
    nombre = Column(String(150), nullable=False)
    estado = Column(String(30), nullable=False, default="disponible")

    taller = relationship("Taller", back_populates="tecnicos")
    servicios = relationship("Servicio", back_populates="tecnico")


class Servicio(Base):
    __tablename__ = "servicios"

    id = Column(Integer, primary_key=True, index=True)
    taller_id = Column(Integer, ForeignKey("talleres.id"), nullable=False)
    tecnico_id = Column(Integer, ForeignKey("tecnicos.id"), nullable=True)
    incidente_id = Column(Integer, ForeignKey("incidentes.id"), unique=True, nullable=False)

    estado = Column(String(30), nullable=False, default="pendiente")
    tiempo_estimado = Column(Integer, nullable=True)
    inicio = Column(DateTime, nullable=True)
    fin = Column(DateTime, nullable=True)

    taller = relationship("Taller", back_populates="servicios")
    tecnico = relationship("Tecnico", back_populates="servicios")
    incidente = relationship("Incidente", back_populates="servicio")

    historiales = relationship("Historial", back_populates="servicio", cascade="all, delete-orphan")
    pago = relationship("Pago", back_populates="servicio", uselist=False, cascade="all, delete-orphan")
    calificacion = relationship("Calificacion", back_populates="servicio", uselist=False, cascade="all, delete-orphan")
    metricas = relationship("Metrica", back_populates="servicio", cascade="all, delete-orphan")


class Evidencia(Base):
    __tablename__ = "evidencias"

    id = Column(Integer, primary_key=True, index=True)
    incidente_id = Column(Integer, ForeignKey("incidentes.id"), nullable=False)
    tipo_archivo = Column(String(50), nullable=False)  # imagen, audio
    url_archivo = Column(String(500), nullable=False)

    incidente = relationship("Incidente", back_populates="evidencias")


class Historial(Base):
    __tablename__ = "historiales"

    id = Column(Integer, primary_key=True, index=True)
    servicio_id = Column(Integer, ForeignKey("servicios.id"), nullable=False)
    estado = Column(String(30), nullable=False)
    descripcion = Column(Text, nullable=False)
    fecha = Column(DateTime, server_default=func.now(), nullable=False)

    servicio = relationship("Servicio", back_populates="historiales")


class Pago(Base):
    __tablename__ = "pagos"

    id = Column(Integer, primary_key=True, index=True)
    servicio_id = Column(Integer, ForeignKey("servicios.id"), unique=True, nullable=False)
    monto = Column(Numeric(10, 2), nullable=False)
    comision = Column(Numeric(10, 2), nullable=False)
    estado = Column(String(30), nullable=False)
    fecha = Column(DateTime, server_default=func.now(), nullable=False)

    servicio = relationship("Servicio", back_populates="pago")


class Calificacion(Base):
    __tablename__ = "calificaciones"

    id = Column(Integer, primary_key=True, index=True)
    servicio_id = Column(Integer, ForeignKey("servicios.id"), unique=True, nullable=False)
    puntuacion = Column(Integer, nullable=False)
    comentarios = Column(Text, nullable=True)

    servicio = relationship("Servicio", back_populates="calificacion")


class Metrica(Base):
    __tablename__ = "metricas"

    id = Column(Integer, primary_key=True, index=True)
    servicio_id = Column(Integer, ForeignKey("servicios.id"), nullable=False)
    tipo = Column(String(100), nullable=False)
    valor = Column(Numeric(10, 2), nullable=False)
    fecha = Column(DateTime, server_default=func.now(), nullable=False)

    servicio = relationship("Servicio", back_populates="metricas")