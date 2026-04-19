import { CommonModule, isPlatformBrowser } from '@angular/common';
import { Component, Inject, OnInit, PLATFORM_ID, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartData } from 'chart.js';
import {
  PanelAdminService,
  DashboardAdminResumen,
  SolicitudAdminReciente,
  UsuarioAdmin
} from '../../services/panel-admin.service';

@Component({
  selector: 'app-panel-admin',
  standalone: true,
  imports: [CommonModule, FormsModule, BaseChartDirective],
  templateUrl: './panel-admin.component.html',
  styleUrl: './panel-admin.component.css'
})
export class PanelAdminComponent implements OnInit {
  private panelAdminService = inject(PanelAdminService);

  admin = {
    nombre: 'admin',
    email: 'admin@emergauto.com'
  };

  selectedMenu = 'dashboard';
  isBrowser = false;

  dashboardCards = {
    usuariosTotales: 0,
    talleresRegistrados: 0,
    solicitudesActivas: 0,
    ingresosMes: 0
  };

  resumen = [
    { titulo: 'Usuarios Totales', valor: 0, detalle: 'Datos reales', icono: '👤' },
    { titulo: 'Talleres Registrados', valor: 0, detalle: 'Datos reales', icono: '🔧' },
    { titulo: 'Solicitudes Activas', valor: 0, detalle: 'En proceso', icono: '📋' },
    { titulo: 'Ingresos del Mes', valor: 'Bs 0.00', detalle: 'Comisiones acumuladas', icono: '💰' }
  ];

  alertas = [
    { texto: 'Solicitudes sin asignación de taller', tipo: 'pendiente' },
    { texto: 'Talleres con baja actividad esta semana', tipo: 'info' },
    { texto: 'Servicios con retraso de atención', tipo: 'urgente' }
  ];

  filtrosSolicitudes = {
    busqueda: '',
    estado: '',
    taller: '',
    fecha: ''
  };

  solicitudesRecientes: SolicitudAdminReciente[] = [];

  talleresTop = [
    { nombre: 'ElectroAuto', servicios: 18, tiempoPromedio: '18 min', calificacion: 4.8 },
    { nombre: 'Rescate Vial', servicios: 15, tiempoPromedio: '20 min', calificacion: 4.7 },
    { nombre: 'Taller Norte', servicios: 11, tiempoPromedio: '24 min', calificacion: 4.5 }
  ];

  filtrosUsuarios = {
    busqueda: '',
    rol: ''
  };

  systemInfo = {
    cpu: 34,
    ram: 68,
    uptime: '24d 7h'
  };

  usuariosSistema: UsuarioAdmin[] = [];

  configuracion = {
    email: true,
    sms: true,
    reportes: false
  };

  adminPerfil = {
    nombre: 'admin',
    apellidos: 'Administrador',
    email: 'dbanegas205@gmail.com',
    telefono: '',
    direccion: 'Santa Cruz, Bolivia',
    ciudad: 'Santa Cruz',
    cargo: 'Administrador'
  };

  public chartOptions: ChartConfiguration['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false }
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { font: { size: 10 } }
      },
      y: {
        beginAtZero: true,
        ticks: { font: { size: 10 } }
      }
    }
  };

  public solicitudesChartData: ChartData<'bar'> = {
    labels: [],
    datasets: [{ data: [] }]
  };

  public usuariosChartData: ChartData<'line'> = {
    labels: [],
    datasets: [{ data: [], tension: 0.35, fill: false }]
  };

  public talleresChartData: ChartData<'bar'> = {
    labels: [],
    datasets: [{ data: [] }]
  };

  public ingresosChartData: ChartData<'bar'> = {
    labels: [],
    datasets: [{ data: [] }]
  };

  mostrarNotificacionesAdmin = false;

  notificacionesAdmin = [
    {
      titulo: 'Solicitud de cambio de cuenta',
      detalle: 'Revisión pendiente de perfil registrado.',
      tiempo: 'Hace 10 min'
    },
    {
      titulo: 'Error reportado',
      detalle: 'Se detectó un evento en el módulo de pagos.',
      tiempo: 'Hace 25 min'
    },
    {
      titulo: 'Usuario en espera',
      detalle: 'Hay solicitudes pendientes de revisión.',
      tiempo: 'Hace 1 h'
    }
  ];

  soporteAbierto = false;
  mensajeSoporte = '';
  grabandoAudio = false;

  mensajesSoporte = [
    {
      autor: 'ia',
      tipo: 'texto',
      contenido: 'Hola, soy el asistente del panel administrativo. Puedo ayudarte con solicitudes, alertas, usuarios y talleres.',
      hora: 'Ahora'
    }
  ];

  constructor(
    private router: Router,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  ngOnInit(): void {
    this.isBrowser = isPlatformBrowser(this.platformId);

    if (this.isBrowser) {
      const adminGuardado = localStorage.getItem('admin_logueado');

      if (adminGuardado) {
        try {
          const data = JSON.parse(adminGuardado);

          this.admin.nombre = data.nombre || 'admin';
          this.admin.email = data.email || 'admin@emergauto.com';

          this.adminPerfil.nombre = data.nombre || 'admin';
          this.adminPerfil.email = data.email || 'admin@emergauto.com';
          this.adminPerfil.telefono = data.telefono || '';
        } catch (error) {
          console.error('Error al leer admin_logueado desde localStorage:', error);
        }
      }
    }

    this.cargarResumenDashboard();
    this.cargarSolicitudesRecientes();
    this.cargarUsuariosSistema();
  }

  cargarResumenDashboard(): void {
    this.panelAdminService.obtenerResumenDashboard().subscribe({
      next: (resp: DashboardAdminResumen) => {
        this.dashboardCards.usuariosTotales = resp.cards.usuarios_totales;
        this.dashboardCards.talleresRegistrados = resp.cards.talleres_registrados;
        this.dashboardCards.solicitudesActivas = resp.cards.solicitudes_activas;
        this.dashboardCards.ingresosMes = resp.cards.ingresos_mes;

        this.resumen = [
          {
            titulo: 'Usuarios Totales',
            valor: this.dashboardCards.usuariosTotales,
            detalle: 'Datos reales',
            icono: '👤'
          },
          {
            titulo: 'Talleres Registrados',
            valor: this.dashboardCards.talleresRegistrados,
            detalle: 'Datos reales',
            icono: '🔧'
          },
          {
            titulo: 'Solicitudes Activas',
            valor: this.dashboardCards.solicitudesActivas,
            detalle: 'En proceso',
            icono: '📋'
          },
          {
            titulo: 'Ingresos del Mes',
            valor: `Bs ${this.dashboardCards.ingresosMes.toFixed(2)}`,
            detalle: 'Comisiones acumuladas',
            icono: '💰'
          }
        ];

        this.usuariosChartData = {
          labels: resp.charts.usuarios.labels,
          datasets: [{ data: resp.charts.usuarios.data, tension: 0.35, fill: false }]
        };

        this.talleresChartData = {
          labels: resp.charts.talleres.labels,
          datasets: [{ data: resp.charts.talleres.data }]
        };

        this.solicitudesChartData = {
          labels: resp.charts.solicitudes.labels,
          datasets: [{ data: resp.charts.solicitudes.data }]
        };

        this.ingresosChartData = {
          labels: resp.charts.ingresos.labels,
          datasets: [{ data: resp.charts.ingresos.data }]
        };
      },
      error: (error) => {
        console.error('Error al cargar dashboard admin:', error);
      }
    });
  }

  cargarSolicitudesRecientes(): void {
    this.panelAdminService.obtenerSolicitudesRecientes().subscribe({
      next: (resp: SolicitudAdminReciente[]) => {
        this.solicitudesRecientes = resp;
      },
      error: (error) => {
        console.error('Error al cargar solicitudes recientes:', error);
        this.solicitudesRecientes = [];
      }
    });
  }

  cargarUsuariosSistema(): void {
    this.panelAdminService.obtenerUsuariosSistema().subscribe({
      next: (resp: UsuarioAdmin[]) => {
        this.usuariosSistema = resp;
      },
      error: (error) => {
        console.error('Error al cargar usuarios del sistema:', error);
        this.usuariosSistema = [];
      }
    });
  }

  get solicitudesFiltradas() {
    return this.solicitudesRecientes.filter((s) => {
      const busqueda = (this.filtrosSolicitudes.busqueda || '').toLowerCase().trim();
      const estado = (this.filtrosSolicitudes.estado || '').trim();
      const taller = (this.filtrosSolicitudes.taller || '').toLowerCase().trim();
      const fecha = (this.filtrosSolicitudes.fecha || '').trim();

      const servicio = (s.servicio || '').toLowerCase();
      const usuario = (s.usuario || '').toLowerCase();
      const nombreTaller = (s.taller || '').toLowerCase();
      const estadoSolicitud = (s.estado || '').trim();
      const fechaSolicitud = (s.fecha || '').trim();

      const coincideBusqueda =
        !busqueda ||
        servicio.includes(busqueda) ||
        usuario.includes(busqueda) ||
        nombreTaller.includes(busqueda);

      const coincideEstado = !estado || estadoSolicitud === estado;
      const coincideTaller = !taller || nombreTaller.includes(taller);
      const coincideFecha = !fecha || fechaSolicitud.startsWith(fecha);

      return coincideBusqueda && coincideEstado && coincideTaller && coincideFecha;
    });
  }

  get usuariosFiltrados() {
    return this.usuariosSistema.filter((u) => {
      const busqueda = (this.filtrosUsuarios.busqueda || '').toLowerCase().trim();
      const rol = (this.filtrosUsuarios.rol || '').trim();

      const nombre = (u.nombre || '').toLowerCase();
      const email = (u.email || '').toLowerCase();
      const rolUsuario = (u.rol || '').trim();

      const coincideBusqueda =
        !busqueda ||
        nombre.includes(busqueda) ||
        email.includes(busqueda);

      const coincideRol = !rol || rolUsuario === rol;

      return coincideBusqueda && coincideRol;
    });
  }

  get totalUsuariosSistema(): number {
    return this.usuariosSistema.length;
  }

  get totalTalleresSistema(): number {
    return this.usuariosSistema.filter(u => u.rol === 'Taller').length;
  }

  get totalUsuariosActivos(): number {
    return this.usuariosSistema.filter(u => u.estado === 'Activo').length;
  }

  limpiarFiltrosSolicitudes(): void {
    this.filtrosSolicitudes = {
      busqueda: '',
      estado: '',
      taller: '',
      fecha: ''
    };
  }

  limpiarFiltrosUsuarios(): void {
    this.filtrosUsuarios = {
      busqueda: '',
      rol: ''
    };
  }

  getEstadoClase(estado: string): string {
    switch (estado) {
      case 'Pendiente':
        return 'estado pendiente';
      case 'Asignado':
        return 'estado asignado';
      case 'Completado':
      case 'Finalizado':
      case 'Cerrado':
        return 'estado completado';
      default:
        return 'estado';
    }
  }

  getEstadoUsuarioClase(estado: string): string {
    switch (estado) {
      case 'Activo':
        return 'user-badge user-active';
      case 'Inactivo':
        return 'user-badge user-inactive';
      default:
        return 'user-badge';
    }
  }

  getRolClase(rol: string): string {
    switch (rol) {
      case 'Taller':
        return 'role-badge role-taller';
      case 'Cliente':
        return 'role-badge role-cliente';
      case 'Administrador':
        return 'role-badge role-admin';
      default:
        return 'role-badge';
    }
  }

  verDetalle(solicitud: SolicitudAdminReciente): void {
    alert(`Viendo detalle de: ${solicitud.servicio}`);
  }

  asignarTaller(solicitud: SolicitudAdminReciente): void {
    solicitud.taller = 'Taller asignado';
    solicitud.estado = 'Asignado';
    alert(`Taller asignado a la solicitud de ${solicitud.usuario}`);
  }

  cambiarEstado(solicitud: SolicitudAdminReciente): void {
    if (solicitud.estado === 'Pendiente') {
      solicitud.estado = 'Asignado';
    } else if (solicitud.estado === 'Asignado') {
      solicitud.estado = 'Completado';
    }
    alert(`Estado actualizado a: ${solicitud.estado}`);
  }

  nuevoUsuario(): void {
    alert('Aquí luego abriremos el formulario para registrar usuarios/talleres.');
  }

  verOpcionesUsuario(usuario: UsuarioAdmin): void {
    alert(`Opciones para: ${usuario.nombre}`);
  }

  mostrarPerfil(): void {
    this.selectedMenu = 'perfil';
  }

  setMenu(menu: string): void {
    this.selectedMenu = menu;
  }

  toggleNotificacionesAdmin(): void {
    this.mostrarNotificacionesAdmin = !this.mostrarNotificacionesAdmin;
  }

  toggleSoporteGlobal(): void {
    this.soporteAbierto = !this.soporteAbierto;
  }

  cerrarSoporteGlobal(): void {
    this.soporteAbierto = false;
  }

  enviarMensajeSoporte(): void {
    const texto = this.mensajeSoporte.trim();
    if (!texto) return;

    this.mensajesSoporte.push({
      autor: 'admin',
      tipo: 'texto',
      contenido: texto,
      hora: 'Ahora'
    });

    const respuesta = this.generarRespuestaSoporte(texto);

    setTimeout(() => {
      this.mensajesSoporte.push({
        autor: 'ia',
        tipo: 'texto',
        contenido: respuesta,
        hora: 'Ahora'
      });
    }, 500);

    this.mensajeSoporte = '';
  }

  onImagenSoporteSeleccionada(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;

    this.mensajesSoporte.push({
      autor: 'admin',
      tipo: 'archivo',
      contenido: `Imagen adjunta: ${file.name}`,
      hora: 'Ahora'
    });

    setTimeout(() => {
      this.mensajesSoporte.push({
        autor: 'ia',
        tipo: 'texto',
        contenido: 'Imagen recibida. Cuando conectemos el backend, podré analizarla automáticamente.',
        hora: 'Ahora'
      });
    }, 400);

    input.value = '';
  }

  toggleAudioSoporte(): void {
    this.grabandoAudio = !this.grabandoAudio;

    if (this.grabandoAudio) {
      this.mensajesSoporte.push({
        autor: 'ia',
        tipo: 'texto',
        contenido: 'Grabación iniciada... por ahora es una simulación visual.',
        hora: 'Ahora'
      });
    } else {
      this.mensajesSoporte.push({
        autor: 'admin',
        tipo: 'archivo',
        contenido: 'Audio enviado',
        hora: 'Ahora'
      });

      setTimeout(() => {
        this.mensajesSoporte.push({
          autor: 'ia',
          tipo: 'texto',
          contenido: 'Audio recibido. Después lo conectaremos a una API real.',
          hora: 'Ahora'
        });
      }, 400);
    }
  }

  generarRespuestaSoporte(texto: string): string {
    const mensaje = texto.toLowerCase();

    if (mensaje.includes('solicitud') || mensaje.includes('solicitudes')) {
      return `Actualmente tienes ${this.dashboardCards.solicitudesActivas} solicitudes activas en el sistema.`;
    }

    if (mensaje.includes('alerta') || mensaje.includes('alertas')) {
      return `Alertas actuales: ${this.alertas.map(a => a.texto).join(' | ')}`;
    }

    if (mensaje.includes('usuario') || mensaje.includes('usuarios')) {
      return `Hay ${this.dashboardCards.usuariosTotales} usuarios registrados en el sistema.`;
    }

    if (mensaje.includes('taller') || mensaje.includes('talleres')) {
      return `Actualmente hay ${this.dashboardCards.talleresRegistrados} talleres registrados.`;
    }

    if (mensaje.includes('ingreso') || mensaje.includes('ingresos')) {
      return `Los ingresos del mes son de Bs ${this.dashboardCards.ingresosMes.toFixed(2)}.`;
    }

    if (mensaje.includes('error')) {
      return 'Puedo ayudarte a revisar errores, alertas y actividad operativa del panel.';
    }

    return 'Puedo ayudarte con solicitudes, alertas, usuarios, talleres, ingresos y soporte administrativo.';
  }

  cerrarSesion(): void {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.removeItem('admin_logueado');
    }

    this.router.navigate(['/admin-login']);
  }
}