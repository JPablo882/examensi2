import { CommonModule, isPlatformBrowser } from '@angular/common';
import { Component, Inject, OnInit, PLATFORM_ID, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartData } from 'chart.js';
import {
  PanelTallerService,
  SolicitudActiva,
  DashboardTallerResumen
} from '../../services/panel-taller.service';

type NotificacionTaller = {
  titulo: string;
  detalle: string;
  tiempo: string;
  fechaBase: string;
};

@Component({
  selector: 'app-panel-taller',
  standalone: true,
  imports: [CommonModule, FormsModule, BaseChartDirective],
  templateUrl: './panel-taller.component.html',
  styleUrl: './panel-taller.component.css'
})
export class PanelTallerComponent implements OnInit {
  taller = {
    nombre: 'Taller Central',
    email: 'taller@emergauto.com'
  };

  selectedMenu = 'dashboard';
  estadoTaller: 'Activo' | 'Inactivo' = 'Activo';
  isBrowser = false;

  private panelTallerService = inject(PanelTallerService);

  filtros = {
    busqueda: '',
    estado: '',
    prioridad: '',
    cliente: '',
    fecha: ''
  };

  filtrosHistorial = {
    busqueda: '',
    estado: '',
    cliente: '',
    fecha: ''
  };

  solicitudesActivas: SolicitudActiva[] = [];

  historial = [
    {
      servicio: 'Grúa y Remolque',
      cliente: 'Mario Suárez',
      estado: 'Completado',
      monto: 'Bs 250',
      fecha: '2026-04-09'
    },
    {
      servicio: 'Apertura de Vehículo',
      cliente: 'Sandra Roca',
      estado: 'Completado',
      monto: 'Bs 120',
      fecha: '2026-04-08'
    },
    {
      servicio: 'Carga de Batería',
      cliente: 'Pedro Gómez',
      estado: 'Completado',
      monto: 'Bs 90',
      fecha: '2026-04-07'
    }
  ];

  perfilTaller = {
    nombre: 'Taller Central',
    encargado: 'No definido',
    email: 'taller@emergauto.com',
    telefono: '',
    direccion: '',
    ciudad: '',
    especialidad: 'Mecánica general y auxilio vehicular'
  };

  dashboardCards = {
    serviciosAsignados: 0,
    serviciosCompletadosMes: 0,
    serviciosActivos: 0,
    ingresosMes: 0
  };

  resumen = [
    { titulo: 'Servicios Asignados', valor: 0, detalle: 'Datos reales', icono: '📋' },
    { titulo: 'Servicios Completados', valor: 0, detalle: 'Este mes', icono: '✅' },
    { titulo: 'Servicios Activos', valor: 0, detalle: 'En proceso', icono: '🕒' },
    { titulo: 'Ingresos del Mes', valor: 'Bs 0.00', detalle: 'Servicios realizados', icono: '💰' }
  ];

  public dashboardChartOptions: ChartConfiguration['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      }
    },
    scales: {
      x: {
        grid: {
          display: false
        },
        ticks: {
          font: {
            size: 10
          }
        }
      },
      y: {
        beginAtZero: true,
        ticks: {
          font: {
            size: 10
          }
        }
      }
    }
  };

  public lineChartOptions: ChartConfiguration['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      }
    },
    scales: {
      x: {
        grid: {
          display: false
        },
        ticks: {
          font: {
            size: 10
          }
        }
      },
      y: {
        beginAtZero: true,
        ticks: {
          font: {
            size: 10
          }
        }
      }
    }
  };

  public serviciosChartData: ChartData<'bar'> = {
    labels: [],
    datasets: [{ label: 'Servicios', data: [] }]
  };

  public completadosChartData: ChartData<'bar'> = {
    labels: [],
    datasets: [{ label: 'Completados', data: [] }]
  };

  public activosChartData: ChartData<'line'> = {
    labels: [],
    datasets: [{
      label: 'Activos',
      data: [],
      tension: 0.35,
      fill: false
    }]
  };

  public ingresosChartData: ChartData<'bar'> = {
    labels: [],
    datasets: [{ label: 'Ingresos', data: [] }]
  };

  mostrarNotificaciones = false;
  notificaciones: NotificacionTaller[] = [];

  constructor(
    private router: Router,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  ngOnInit(): void {
    this.isBrowser = isPlatformBrowser(this.platformId);

    if (this.isBrowser) {
      const tallerGuardado = localStorage.getItem('taller_logueado');

      if (tallerGuardado) {
        try {
          const data = JSON.parse(tallerGuardado);

          this.taller.nombre = data.nombre || 'Taller Central';
          this.taller.email = data.email || 'taller@emergauto.com';

          this.perfilTaller.nombre = data.nombre || 'Taller Central';
          this.perfilTaller.encargado = data.nombre || 'No definido';
          this.perfilTaller.email = data.email || 'taller@emergauto.com';
          this.perfilTaller.telefono = data.telefono || '';
        } catch (error) {
          console.error('Error al leer taller_logueado:', error);
        }
      }

      if (this.taller.email) {
        this.cargarSolicitudesYNotificaciones();
        this.cargarResumenDashboard();
      }
    }
  }

  cargarSolicitudesYNotificaciones(): void {
    this.panelTallerService.obtenerSolicitudesActivas(this.taller.email).subscribe({
      next: (resp: SolicitudActiva[]) => {
        this.solicitudesActivas = resp;
        this.notificaciones = this.generarNotificacionesDesdeSolicitudes(resp);
      },
      error: (error) => {
        console.error('Error al cargar solicitudes activas:', error);
        this.solicitudesActivas = [];
        this.notificaciones = [];
      }
    });
  }

  cargarResumenDashboard(): void {
    this.panelTallerService.obtenerResumenDashboard(this.taller.email).subscribe({
      next: (resp: DashboardTallerResumen) => {
        this.dashboardCards.serviciosAsignados = resp.cards.servicios_asignados;
        this.dashboardCards.serviciosCompletadosMes = resp.cards.servicios_completados_mes;
        this.dashboardCards.serviciosActivos = resp.cards.servicios_activos;
        this.dashboardCards.ingresosMes = resp.cards.ingresos_mes;

        this.serviciosChartData = {
          labels: resp.charts.servicios.labels,
          datasets: [
            {
              label: 'Servicios',
              data: resp.charts.servicios.data
            }
          ]
        };

        this.completadosChartData = {
          labels: resp.charts.completados.labels,
          datasets: [
            {
              label: 'Completados',
              data: resp.charts.completados.data
            }
          ]
        };

        this.activosChartData = {
          labels: resp.charts.activos.labels,
          datasets: [
            {
              label: 'Activos',
              data: resp.charts.activos.data,
              tension: 0.35,
              fill: false
            }
          ]
        };

        this.ingresosChartData = {
          labels: resp.charts.ingresos.labels,
          datasets: [
            {
              label: 'Ingresos',
              data: resp.charts.ingresos.data
            }
          ]
        };
      },
      error: (error) => {
        console.error('Error al cargar resumen del dashboard:', error);
      }
    });
  }

  generarNotificacionesDesdeSolicitudes(solicitudes: SolicitudActiva[]): NotificacionTaller[] {
    const ordenadas = [...solicitudes].sort((a, b) => {
      const fechaA = this.convertirAFecha(a.fecha).getTime();
      const fechaB = this.convertirAFecha(b.fecha).getTime();
      return fechaB - fechaA;
    });

    return ordenadas.slice(0, 5).map((s) => ({
      titulo: 'Nueva solicitud asignada',
      detalle: `${s.servicio} - ${s.cliente}`,
      tiempo: this.calcularTiempoRelativo(s.fecha),
      fechaBase: s.fecha
    }));
  }

  convertirAFecha(fecha: string): Date {
    if (!fecha) return new Date();

    const fechaNormalizada = fecha.includes('T')
      ? fecha
      : fecha.includes(' ')
        ? fecha.replace(' ', 'T')
        : `${fecha}T00:00:00`;

    const fechaConvertida = new Date(fechaNormalizada);

    return isNaN(fechaConvertida.getTime()) ? new Date() : fechaConvertida;
  }

  calcularTiempoRelativo(fecha: string): string {
    const fechaSolicitud = this.convertirAFecha(fecha);
    const ahora = new Date();

    const diferenciaMs = ahora.getTime() - fechaSolicitud.getTime();
    const diferenciaMin = Math.floor(diferenciaMs / (1000 * 60));
    const diferenciaHoras = Math.floor(diferenciaMin / 60);
    const diferenciaDias = Math.floor(diferenciaHoras / 24);

    if (diferenciaMin < 1) return 'Hace 1 min';
    if (diferenciaMin < 60) return `Hace ${diferenciaMin} min`;
    if (diferenciaHoras < 24) return `Hace ${diferenciaHoras} h`;
    return `Hace ${diferenciaDias} día${diferenciaDias > 1 ? 's' : ''}`;
  }

  toggleEstadoTaller(): void {
    this.estadoTaller = this.estadoTaller === 'Activo' ? 'Inactivo' : 'Activo';
  }

  getPrioridadClase(prioridad: string): string {
    switch (prioridad) {
      case 'Alta':
        return 'prioridad alta';
      case 'Media':
        return 'prioridad media';
      case 'Baja':
        return 'prioridad baja';
      default:
        return 'prioridad';
    }
  }

  get solicitudesFiltradas() {
    return this.solicitudesActivas.filter((s) => {
      const busqueda = (this.filtros.busqueda || '').toLowerCase().trim();
      const estado = (this.filtros.estado || '').trim();
      const prioridad = (this.filtros.prioridad || '').trim();
      const cliente = (this.filtros.cliente || '').toLowerCase().trim();
      const fecha = (this.filtros.fecha || '').trim();

      const codigo = (s.codigo || '').toLowerCase();
      const servicio = (s.servicio || '').toLowerCase();
      const nombreCliente = (s.cliente || '').toLowerCase();
      const ubicacion = (s.ubicacion || '').toLowerCase();
      const vehiculo = (s.vehiculo || '').toLowerCase();
      const estadoSolicitud = (s.estado || '').trim();
      const prioridadSolicitud = (s.prioridad || '').trim();
      const fechaSolicitud = (s.fecha || '').trim();

      const coincideBusqueda =
        !busqueda ||
        codigo.includes(busqueda) ||
        servicio.includes(busqueda) ||
        nombreCliente.includes(busqueda) ||
        ubicacion.includes(busqueda) ||
        vehiculo.includes(busqueda);

      const coincideEstado = !estado || estadoSolicitud === estado;
      const coincidePrioridad = !prioridad || prioridadSolicitud === prioridad;
      const coincideCliente = !cliente || nombreCliente.includes(cliente);
      const coincideFecha = !fecha || fechaSolicitud.startsWith(fecha);

      return (
        coincideBusqueda &&
        coincideEstado &&
        coincidePrioridad &&
        coincideCliente &&
        coincideFecha
      );
    });
  }

  get historialFiltrado() {
    return this.historial.filter((h) => {
      const busqueda = (this.filtrosHistorial.busqueda || '').toLowerCase().trim();
      const estado = (this.filtrosHistorial.estado || '').trim();
      const cliente = (this.filtrosHistorial.cliente || '').toLowerCase().trim();
      const fecha = (this.filtrosHistorial.fecha || '').trim();

      const servicio = (h.servicio || '').toLowerCase();
      const nombreCliente = (h.cliente || '').toLowerCase();
      const estadoHistorial = (h.estado || '').trim();
      const monto = (h.monto || '').toLowerCase();
      const fechaHistorial = (h.fecha || '').trim();

      const coincideBusqueda =
        !busqueda ||
        servicio.includes(busqueda) ||
        nombreCliente.includes(busqueda) ||
        monto.includes(busqueda);

      const coincideEstado = !estado || estadoHistorial === estado;
      const coincideCliente = !cliente || nombreCliente.includes(cliente);
      const coincideFecha = !fecha || fechaHistorial === fecha;

      return (
        coincideBusqueda &&
        coincideEstado &&
        coincideCliente &&
        coincideFecha
      );
    });
  }

  limpiarFiltros(): void {
    this.filtros = {
      busqueda: '',
      estado: '',
      prioridad: '',
      cliente: '',
      fecha: ''
    };
  }

  limpiarFiltrosHistorial(): void {
    this.filtrosHistorial = {
      busqueda: '',
      estado: '',
      cliente: '',
      fecha: ''
    };
  }

  setMenu(menu: string): void {
    this.selectedMenu = menu;
  }

  mostrarPerfil(): void {
    this.selectedMenu = 'perfil';
  }

  aceptarSolicitud(solicitud: any): void {
    solicitud.estado = 'Aceptada';
    alert(`Solicitud ${solicitud.codigo} aceptada correctamente.`);
  }

  asignarTecnico(solicitud: any): void {
    solicitud.tecnico = 'Técnico Asignado';
    solicitud.telefonoTecnico = '70000000';
    solicitud.estado = 'Asignado';
    alert(`Se asignó un técnico a la solicitud ${solicitud.codigo}.`);
  }

  actualizarEstado(solicitud: any): void {
    if (solicitud.estado === 'Asignado') {
      solicitud.estado = 'En proceso';
    } else if (solicitud.estado === 'En proceso') {
      solicitud.estado = 'Finalizado';
    } else if (solicitud.estado === 'Pendiente') {
      solicitud.estado = 'Asignado';
    }

    alert(`Estado actualizado: ${solicitud.codigo} → ${solicitud.estado}`);
    this.notificaciones = this.generarNotificacionesDesdeSolicitudes(this.solicitudesActivas);
  }

  cerrarServicio(solicitud: any): void {
    solicitud.estado = 'Cerrado';
    alert(`Servicio ${solicitud.codigo} cerrado correctamente.`);
    this.notificaciones = this.generarNotificacionesDesdeSolicitudes(this.solicitudesActivas);
  }

  getEstadoClase(estado: string): string {
    switch (estado) {
      case 'Pendiente':
        return 'estado pendiente';
      case 'Aceptada':
        return 'estado aceptada';
      case 'Asignado':
        return 'estado asignado';
      case 'En proceso':
        return 'estado proceso';
      case 'Finalizado':
        return 'estado finalizado';
      case 'Cerrado':
        return 'estado cerrado';
      default:
        return 'estado';
    }
  }

  toggleNotificaciones(): void {
    this.mostrarNotificaciones = !this.mostrarNotificaciones;
  }

  cerrarSesion(): void {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.removeItem('taller_logueado');
    }

    this.router.navigate(['/login']);
  }
}