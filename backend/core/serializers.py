from rest_framework import serializers
from .models import (
    Rol, Permiso, RolPermiso, Usuario, Taller, Tecnico,
    Vehiculo, Incidente, Evidencia, Servicio,
    Historial, Pago, Calificacion, Metrica
)


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = '__all__'


class PermisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permiso
        fields = '__all__'


class RolPermisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolPermiso
        fields = '__all__'


class UsuarioSerializer(serializers.ModelSerializer):
    fecha_registro = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S", read_only=True)

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'nombre', 'email',
            'telefono', 'fecha_registro', 'rol',
            'first_name', 'last_name', 'is_active'
        ]


class TallerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Taller
        fields = '__all__'


class TecnicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tecnico
        fields = '__all__'


class VehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = '__all__'


class IncidenteSerializer(serializers.ModelSerializer):
    fecha = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S", read_only=True)

    class Meta:
        model = Incidente
        fields = '__all__'


class EvidenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evidencia
        fields = '__all__'


class ServicioSerializer(serializers.ModelSerializer):
    inicio = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S", read_only=True)
    fin = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S", read_only=True, allow_null=True)

    class Meta:
        model = Servicio
        fields = '__all__'


class HistorialSerializer(serializers.ModelSerializer):
    fecha = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S", read_only=True)

    class Meta:
        model = Historial
        fields = '__all__'


class PagoSerializer(serializers.ModelSerializer):
    fecha = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S", read_only=True)

    class Meta:
        model = Pago
        fields = '__all__'


class CalificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calificacion
        fields = '__all__'


class MetricaSerializer(serializers.ModelSerializer):
    fecha = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S", read_only=True)

    class Meta:
        model = Metrica
        fields = '__all__'