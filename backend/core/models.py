from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

#Tabla Rol
class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

#Tabla Permiso
class Permiso(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

#Tabla RolPermiso
class RolPermiso(models.Model):
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, related_name='roles_permisos')#llave foraneas
    permiso = models.ForeignKey(Permiso, on_delete=models.CASCADE, related_name='permisos_roles')#llaves foraneas

    class Meta:
        unique_together = ('rol', 'permiso')#unifica 

    def __str__(self):
        return f"{self.rol.nombre} - {self.permiso.nombre}"

#Tabla Usuario falta contraseña y xq rol
class Usuario(AbstractUser):
    nombre = models.CharField(max_length=150, default='sin nombre')
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT, related_name='usuarios', null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.rol.nombre})" if self.rol else self.username 


class Taller(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='taller')
    nombre = models.CharField(max_length=150)
    direccion = models.CharField(max_length=255)
    ubicacion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    estado = models.CharField(max_length=30)

    def __str__(self):
        return self.nombre


class Tecnico(models.Model):
    taller = models.ForeignKey(Taller, on_delete=models.CASCADE, related_name='tecnicos')
    nombre = models.CharField(max_length=150)
    estado = models.CharField(max_length=30)

    def __str__(self):
        return self.nombre


class Vehiculo(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='vehiculos')
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    placa = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.placa} - {self.marca} {self.modelo}"


class Incidente(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='incidentes')
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name='incidentes')
    descripcion = models.TextField()
    ubicacion = models.CharField(max_length=255)
    tipo_problema = models.CharField(max_length=100)
    prioridad = models.CharField(max_length=30)
    estado = models.CharField(max_length=30)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Incidente {self.id}"


class Servicio(models.Model):
    taller = models.ForeignKey(Taller, on_delete=models.CASCADE, related_name='servicios')
    tecnico = models.ForeignKey(Tecnico, on_delete=models.CASCADE, related_name='servicios')
    incidente = models.OneToOneField(Incidente, on_delete=models.CASCADE, related_name='servicio')
    estado = models.CharField(max_length=30)
    tiempo_estimado = models.IntegerField()
    inicio = models.DateTimeField()
    fin = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Servicio {self.id}"


class Evidencia(models.Model):
    incidente = models.ForeignKey(Incidente, on_delete=models.CASCADE, related_name='evidencias')
    tipo_imagen_audio = models.CharField(max_length=50)
    url_archivo = models.URLField(max_length=500)

    def __str__(self):
        return f"Evidencia {self.id}"


class Historial(models.Model):
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name='historiales')
    estado = models.CharField(max_length=30)
    descripcion = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Historial {self.id}"


class Pago(models.Model):
    servicio = models.OneToOneField(Servicio, on_delete=models.CASCADE, related_name='pago')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    comision = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=30)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pago {self.id}"


class Calificacion(models.Model):
    servicio = models.OneToOneField(Servicio, on_delete=models.CASCADE, related_name='calificacion')
    puntuacion = models.IntegerField()
    comentarios = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Calificación {self.id}"


class Metrica(models.Model):
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name='metricas')
    tipo = models.CharField(max_length=100)
    calor = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Métrica {self.id}"