from django.shortcuts import render
from django.db import transaction

# Create your views here.
from rest_framework import viewsets
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status



from .models import (
    Rol, Permiso, RolPermiso, Usuario, Taller, Tecnico,
    Vehiculo, Incidente, Evidencia, Servicio,
    Historial, Pago, Calificacion, Metrica
)
from .serializers import (
    RolSerializer, PermisoSerializer, RolPermisoSerializer, UsuarioSerializer,
    TallerSerializer, TecnicoSerializer, VehiculoSerializer, IncidenteSerializer,
    EvidenciaSerializer, ServicioSerializer, HistorialSerializer,
    PagoSerializer, CalificacionSerializer, MetricaSerializer
)


class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer


class PermisoViewSet(viewsets.ModelViewSet):
    queryset = Permiso.objects.all()
    serializer_class = PermisoSerializer


class RolPermisoViewSet(viewsets.ModelViewSet):
    queryset = RolPermiso.objects.all()
    serializer_class = RolPermisoSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer


class TallerViewSet(viewsets.ModelViewSet):
    queryset = Taller.objects.all()
    serializer_class = TallerSerializer


class TecnicoViewSet(viewsets.ModelViewSet):
    queryset = Tecnico.objects.all()
    serializer_class = TecnicoSerializer


class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = Vehiculo.objects.all()
    serializer_class = VehiculoSerializer


class IncidenteViewSet(viewsets.ModelViewSet):
    queryset = Incidente.objects.all()
    serializer_class = IncidenteSerializer


class EvidenciaViewSet(viewsets.ModelViewSet):
    queryset = Evidencia.objects.all()
    serializer_class = EvidenciaSerializer


class ServicioViewSet(viewsets.ModelViewSet):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer


class HistorialViewSet(viewsets.ModelViewSet):
    queryset = Historial.objects.all()
    serializer_class = HistorialSerializer


class PagoViewSet(viewsets.ModelViewSet):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer


class CalificacionViewSet(viewsets.ModelViewSet):
    queryset = Calificacion.objects.all()
    serializer_class = CalificacionSerializer


class MetricaViewSet(viewsets.ModelViewSet):
    queryset = Metrica.objects.all()
    serializer_class = MetricaSerializer


class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        email = (request.data.get('email') or '').strip()
        password = request.data.get('password') or ''
        access_type = (request.data.get('access_type') or 'taller').strip().lower()

        if not email or not password:
            return Response(
                {'detail': 'Email y contraseña son obligatorios.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            usuario_email = Usuario.objects.get(email__iexact=email)
        except Usuario.DoesNotExist:
            return Response(
                {'detail': 'Credenciales inválidas.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        user = authenticate(
            request,
            username=usuario_email.username,
            password=password
        )

        if user is None:
            return Response(
                {'detail': 'Credenciales inválidas.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        rol_nombre = ''
        if getattr(user, 'rol', None) and user.rol.nombre:
            rol_nombre = user.rol.nombre.strip().lower()

        es_admin = user.is_staff or user.is_superuser or rol_nombre == 'administrador'

        if access_type == 'admin':
            if not es_admin:
                return Response(
                    {'detail': 'Esta cuenta no tiene acceso administrativo.'},
                    status=status.HTTP_403_FORBIDDEN
                )

        elif access_type == 'taller':
            if es_admin:
                return Response(
                    {'detail': 'Esta cuenta debe usar el acceso administrativo.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            if rol_nombre != 'taller':
                return Response(
                    {'detail': 'Esta cuenta no tiene acceso de taller en la web.'},
                    status=status.HTTP_403_FORBIDDEN
                )

        else:
            return Response(
                {'detail': 'Tipo de acceso no válido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            'message': 'Login correcto',
            'user': {
                'id': user.id,
                'username': user.username,
                'nombre': getattr(user, 'nombre', '') or user.get_full_name() or user.username,
                'email': user.email,
                'rol': user.rol.nombre if getattr(user, 'rol', None) else None,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
            }
        }, status=status.HTTP_200_OK)
        

class RegisterTallerAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        nombre_completo = (request.data.get('nombreCompleto') or '').strip()
        email = (request.data.get('email') or '').strip().lower()
        telefono = (request.data.get('telefono') or '').strip()
        password = request.data.get('password') or ''
        confirm_password = request.data.get('confirmPassword') or ''
        acepta_terminos = request.data.get('aceptaTerminos', False)

        if not nombre_completo or not email or not telefono or not password or not confirm_password:
            return Response(
                {'detail': 'Todos los campos son obligatorios.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if password != confirm_password:
            return Response(
                {'detail': 'Las contraseñas no coinciden.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not acepta_terminos:
            return Response(
                {'detail': 'Debes aceptar los términos y condiciones.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if Usuario.objects.filter(email__iexact=email).exists():
            return Response(
                {'detail': 'Ya existe un usuario con ese email.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            rol_taller = Rol.objects.get(nombre__iexact='Taller')
        except Rol.DoesNotExist:
            return Response(
                {'detail': 'No existe el rol Taller en la base de datos.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        partes_nombre = nombre_completo.split()
        first_name = partes_nombre[0] if partes_nombre else ''
        last_name = ' '.join(partes_nombre[1:]) if len(partes_nombre) > 1 else ''

        base_username = email.split('@')[0]
        username = base_username
        contador = 1

        while Usuario.objects.filter(username=username).exists():
            username = f'{base_username}{contador}'
            contador += 1

        with transaction.atomic():
            user = Usuario.objects.create_user(
                username=username,
                email=email,
                password=password,
                nombre=nombre_completo,
                telefono=telefono,
                rol=rol_taller,
                first_name=first_name,
                last_name=last_name,
                is_active=True
            )

        return Response({
            'message': 'Taller registrado correctamente.',
            'user': {
                'id': user.id,
                'username': user.username,
                'nombre': user.nombre,
                'email': user.email,
                'telefono': user.telefono,
                'rol': user.rol.nombre if user.rol else None
            }
        }, status=status.HTTP_201_CREATED)