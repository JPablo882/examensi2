
# Register your models here.
#from django.contrib import admin
#from django.contrib.auth.admin import UserAdmin
#from .models import Usuario

#admin.site.register(Usuario, UserAdmin)


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Rol,
    Permiso,
    RolPermiso,
    Usuario,
    Taller,
    Tecnico,
    Vehiculo,
    Incidente,
    Evidencia,
    Servicio,
    Historial,
    Pago,
    Calificacion,
    Metrica,
)

class UsuarioAdminCustom(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Campos personalizados', {
            'fields': ('nombre', 'telefono', 'rol', 'fecha_registro')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Campos personalizados', {
            'fields': ('nombre', 'telefono', 'rol')
        }),
    )


admin.site.register(Rol)
admin.site.register(Permiso)
admin.site.register(RolPermiso)
admin.site.register(Usuario, UserAdmin)
admin.site.register(Taller)
admin.site.register(Tecnico)
admin.site.register(Vehiculo)
admin.site.register(Incidente)
admin.site.register(Evidencia)
admin.site.register(Servicio)
admin.site.register(Historial)
admin.site.register(Pago)
admin.site.register(Calificacion)
admin.site.register(Metrica)