import { CommonModule, isPlatformBrowser } from '@angular/common';
import { Component, Inject, OnInit, PLATFORM_ID, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartData } from 'chart.js';
import {
  PanelTallerService,
  SolicitudActiva,
  DashboardTallerResumen,
  HistorialTallerItem,
  TecnicoTaller,
  AsignacionTecnicoResponse,
  IncidenteDisponible,
  RegistrarServicioPayload
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

  tallerId: number | null = null;

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

  serviciosActivos: SolicitudActiva[] = [];
  servicioSeleccionadoId: number | null = null;
  estadoSeleccionado: string = 'pendiente';
  mostrarModalActualizarEstado: boolean = false;

  estadosDisponibles = [
    { valor: 'pendiente', label: 'Pendiente' },
    { valor: 'aceptada', label: 'Aceptada' },
    { valor: 'asignado', label: 'Asignado' },
    { valor: 'en_proceso', label: 'En Proceso' },
    { valor: 'finalizado', label: 'Finalizado' },
    { valor: 'cerrado', label: 'Cerrado' }
  ];

  solicitudesActivas: SolicitudActiva[] = [];
  historial: HistorialTallerItem[] = [];

  mostrarModalAsignacion = false;
  tecnicosDisponibles: TecnicoTaller[] = [];
  solicitudSeleccionadaId: number | null = null;
  tecnicoSeleccionadoId: number | null = null;
  cargandoTecnicos = false;
  guardandoAsignacion = false;

  mostrarModalRegistroServicio = false;
  incidentesDisponibles: IncidenteDisponible[] = [];
  cargandoIncidentes = false;
  guardandoServicio = false;

  registroServicio = {
    incidente_id: null as number | null,
    tecnico_id: null as number | null,
    tiempo_estimado: null as number | null
  };

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
  servicios_asignados: 0,
  servicios_completados_mes: 0,
  servicios_activos: 0,
  ingresos_mes: 0
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
    plugins: { legend: { display: false } },
    scales: {
      x: { grid: { display: false }, ticks: { font: { size: 10 } } },
      y: { beginAtZero: true, ticks: { font: { size: 10 } } }
    }
  };

  public lineChartOptions: ChartConfiguration['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      x: { grid: { display: false }, ticks: { font: { size: 10 } } },
      y: { beginAtZero: true, ticks: { font: { size: 10 } } }
    }
  };

  public serviciosChartData: ChartData<'bar'> = { labels: [], datasets: [{ label: 'Servicios', data: [] }] };
  public completadosChartData: ChartData<'bar'> = { labels: [], datasets: [{ label: 'Completados', data: [] }] };
  public activosChartData: ChartData<'line'> = { labels: [], datasets: [{ label: 'Activos', data: [], tension: 0.35, fill: false }] };
  public ingresosChartData: ChartData<'bar'> = { labels: [], datasets: [{ label: 'Ingresos', data: [] }] };

  mostrarNotificaciones = false;
  notificaciones: NotificacionTaller[] = [];

  ingresosTotales: number = 0;
  comisionesTotales: number = 0;
  netoRecibir: number = 0;
  pagosHistorial: any[] = [];

  saldoBilletera: number = 0;
  bonos: number = 0;
  historialTransacciones: any[] = [];
  mostrarModalRecarga: boolean = false;
  montoRecarga: number = 30;
  recargaRecurrente: boolean = false;
  recargando: boolean = false;

  mostrarModalEditarPerfil: boolean = false;
  guardandoPerfil: boolean = false;
  perfilEditado = {
    nombre: '',
    encargado: '',
    email: '',
    telefono: '',
    direccion: '',
    ciudad: '',
    especialidad: ''
  };

  // ==================== VARIABLES PARA TÉCNICOS ====================
  nombreTecnico: string = '';
  tecnicos: any[] = [];
  registrando: boolean = false;

  seccionesAbiertas: any = {
    infoTaller: true,
    contacto: true,
    ubicacion: true,
    especialidad: true
  };

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
          console.log('Datos del taller en localStorage:', data);

          this.tallerId = data.id || null;
          console.log('🎯 ID del taller logueado:', this.tallerId); // Debe mostrar 2
          this.taller.nombre = data.nombre || 'Taller Central';
          this.taller.email = data.email || 'taller@emergauto.com';

          this.perfilTaller.nombre = data.nombre || 'Taller Central';
          this.perfilTaller.email = data.email || 'taller@emergauto.com';
          this.perfilTaller.telefono = data.telefono || '78546214';
          this.perfilTaller.direccion = data.direccion || 'Av. Virgen de Luján 123';
          this.perfilTaller.ciudad = data.ubicacion || 'Santa Cruz de la Sierra';
          this.perfilTaller.encargado = data.encargado || data.nombre || 'Carlos Pérez';
          this.perfilTaller.especialidad = 'Mecánica general y auxilio vehicular';
          
        } catch (error) {
          console.error('Error al leer taller_logueado:', error);
        }
      }

      if (this.taller.email) {
        this.cargarSolicitudesYNotificaciones();
        this.cargarResumenDashboard();
        this.cargarHistorial();
        this.cargarServiciosActivos();
        this.cargarMontos();
       // this.cargarBilletera();
        this.cargarNotificaciones();
        this.cargarTecnicos(); // Cargar técnicos
        this.cargarBilletera();  // ← USA localStorage
      }
    }
  }

  cargarMontos(): void {
  console.log('📡 Cargando montos...');
  
  this.panelTallerService.obtenerMontosTaller(this.taller.email).subscribe({
    next: (resp: any) => {
      console.log('✅ Respuesta del backend:', resp);
      
      this.ingresosTotales = resp.ingresos_totales;
      this.comisionesTotales = resp.comisiones_totales;
      this.netoRecibir = resp.neto_recibir;
      this.pagosHistorial = resp.pagos;
      
      console.log('📊 pagosHistorial:', this.pagosHistorial);
      console.log('📊 Cantidad de pagos:', this.pagosHistorial?.length);
    },
    error: (error) => {
      console.error('❌ Error:', error);
    }
  });
}

  cargarNotificaciones(): void {
    this.panelTallerService.obtenerNotificacionesTaller(this.taller.email).subscribe({
      next: (resp: any[]) => {
        console.log('📢 Notificaciones recibidas:', resp);
        this.notificaciones = resp.map(n => ({
          titulo: n.titulo,
          detalle: n.detalle,
          tiempo: n.tiempo,
          fechaBase: n.fecha
        }));
      },
      error: (error) => {
        console.error('Error al cargar notificaciones:', error);
      }
    });
  }

 cargarBilletera(): void {
  const transacciones = [
    { fecha: '2026-04-23', descripcion: 'Recarga con VISA', monto: 30.00, tipo: 'ingreso', estado: 'completado' },
    { fecha: '2026-04-22', descripcion: 'Pago servicio SRV-0003', monto: 350.00, tipo: 'ingreso', estado: 'completado' },
    { fecha: '2026-04-21', descripcion: 'Pago servicio SRV-0006', monto: 450.00, tipo: 'ingreso', estado: 'completado' }
  ];
  
  this.historialTransacciones = transacciones;
  
  // Calcular saldo total
  this.saldoBilletera = transacciones.reduce((total, t) => total + t.monto, 0);
  this.bonos = 0;
}

  abrirModalRecarga(): void {
    this.mostrarModalRecarga = true;
    this.montoRecarga = 30;
    this.recargaRecurrente = false;
  }

  cerrarModalRecarga(): void {
    this.mostrarModalRecarga = false;
    this.recargando = false;
  }

  setMontoRecarga(monto: number): void {
    this.montoRecarga = monto;
  }

  calcularViajes(monto: number): number {
    if (!monto) return 0;
    return Math.floor(monto / 1.88);
  }

  // Recargar saldo
confirmarRecarga(): void {
  if (!this.montoRecarga || this.montoRecarga < 10) {
    alert('Ingresa un monto válido (mínimo Bs 10)');
    return;
  }

  this.recargando = true;

  // Actualizar saldo localmente
  this.saldoBilletera += this.montoRecarga;
  localStorage.setItem('billetera_saldo', this.saldoBilletera.toString());
  
  // Agregar transacción
  const nuevaTransaccion = {
    fecha: new Date().toISOString().split('T')[0],
    descripcion: `Recarga con VISA de Bs ${this.montoRecarga}`,
    monto: this.montoRecarga,
    tipo: 'ingreso',
    estado: 'completado'
  };
  
  this.historialTransacciones.unshift(nuevaTransaccion);
  localStorage.setItem('billetera_transacciones', JSON.stringify(this.historialTransacciones));
  
  alert(`✅ Recarga exitosa! Se añadieron Bs ${this.montoRecarga} a tu saldo`);
  this.cerrarModalRecarga();
  this.recargando = false;
 }

  editarPerfil(): void {
    this.perfilEditado = {
      nombre: '',
      encargado: '',
      email: '',
      telefono: '',
      direccion: '',
      ciudad: '',
      especialidad: ''
    };
    this.mostrarModalEditarPerfil = true;
  }

  toggleSeccion(seccion: string): void {
    this.seccionesAbiertas[seccion] = !this.seccionesAbiertas[seccion];
  }

  cerrarModalEditarPerfil(): void {
    this.mostrarModalEditarPerfil = false;
    this.perfilEditado = {
      nombre: '',
      encargado: '',
      email: '',
      telefono: '',
      direccion: '',
      ciudad: '',
      especialidad: ''
    };
    this.guardandoPerfil = false;
  }

  guardarCambiosPerfil(): void {
    this.guardandoPerfil = true;
    
    const datosActualizar: any = {};
    
    if (this.perfilEditado.nombre) datosActualizar.nombre = this.perfilEditado.nombre;
    if (this.perfilEditado.encargado) datosActualizar.encargado = this.perfilEditado.encargado;
    if (this.perfilEditado.email) datosActualizar.email = this.perfilEditado.email;
    if (this.perfilEditado.telefono) datosActualizar.telefono = this.perfilEditado.telefono;
    if (this.perfilEditado.direccion) datosActualizar.direccion = this.perfilEditado.direccion;
    if (this.perfilEditado.ciudad) datosActualizar.ciudad = this.perfilEditado.ciudad;
    if (this.perfilEditado.especialidad) datosActualizar.especialidad = this.perfilEditado.especialidad;
    
    if (Object.keys(datosActualizar).length === 0) {
      alert('No se ingresaron cambios para actualizar');
      this.guardandoPerfil = false;
      this.cerrarModalEditarPerfil();
      return;
    }
    
    this.panelTallerService.actualizarPerfilTaller(this.taller.email, datosActualizar).subscribe({
      next: (resp: any) => {
        alert('✅ Perfil actualizado correctamente');
        
        if (datosActualizar.nombre) this.perfilTaller.nombre = datosActualizar.nombre;
        if (datosActualizar.encargado) this.perfilTaller.encargado = datosActualizar.encargado;
        if (datosActualizar.email) this.perfilTaller.email = datosActualizar.email;
        if (datosActualizar.telefono) this.perfilTaller.telefono = datosActualizar.telefono;
        if (datosActualizar.direccion) this.perfilTaller.direccion = datosActualizar.direccion;
        if (datosActualizar.ciudad) this.perfilTaller.ciudad = datosActualizar.ciudad;
        if (datosActualizar.especialidad) this.perfilTaller.especialidad = datosActualizar.especialidad;
        
        const tallerGuardado = localStorage.getItem('taller_logueado');
        if (tallerGuardado) {
          const data = JSON.parse(tallerGuardado);
          if (datosActualizar.nombre) data.nombre = datosActualizar.nombre;
          if (datosActualizar.email) data.email = datosActualizar.email;
          if (datosActualizar.telefono) data.telefono = datosActualizar.telefono;
          if (datosActualizar.direccion) data.direccion = datosActualizar.direccion;
          if (datosActualizar.ciudad) data.ubicacion = datosActualizar.ciudad;
          localStorage.setItem('taller_logueado', JSON.stringify(data));
        }
        
        this.guardandoPerfil = false;
        this.cerrarModalEditarPerfil();
      },
      error: (error) => {
        console.error('Error al actualizar perfil:', error);
        alert(error.error?.detail || '❌ Error al actualizar el perfil');
        this.guardandoPerfil = false;
      }
    });
  }

  cargarServiciosActivos(): void {
    this.panelTallerService.obtenerSolicitudesActivas(this.taller.email).subscribe({
      next: (resp: SolicitudActiva[]) => {
        this.serviciosActivos = resp;
      },
      error: (error) => console.error('Error:', error)
    });
  }

  cargarSolicitudesYNotificaciones(): void {
    this.panelTallerService.obtenerSolicitudesActivas(this.taller.email).subscribe({
      next: (resp: SolicitudActiva[]) => {
        this.solicitudesActivas = resp;
        this.notificaciones = this.generarNotificacionesDesdeSolicitudes(resp);
      },
      error: (error) => {
        console.error('Error:', error);
        this.solicitudesActivas = [];
        this.notificaciones = [];
      }
    });
  }

  abrirModalActualizarEstado(servicio?: SolicitudActiva): void {
    if (servicio) {
      this.servicioSeleccionadoId = servicio.id;
      this.estadoSeleccionado = servicio.estado.toLowerCase();
    }
    this.mostrarModalActualizarEstado = true;
  }

  cerrarModalActualizarEstado(): void {
    this.mostrarModalActualizarEstado = false;
    this.servicioSeleccionadoId = null;
    this.estadoSeleccionado = 'pendiente';
  }

  confirmarActualizarEstado(): void {
    if (!this.servicioSeleccionadoId) {
      alert('No hay servicio seleccionado');
      return;
    }

    if (!this.estadoSeleccionado) {
      alert('Por favor, seleccione un estado');
      return;
    }

    this.panelTallerService.actualizarEstadoServicio(this.servicioSeleccionadoId, this.estadoSeleccionado).subscribe({
      next: (resp) => {
        alert(resp.message || 'Estado actualizado correctamente');
        this.cerrarModalActualizarEstado();
        this.cargarServiciosActivos();
        this.cargarSolicitudesYNotificaciones();
        this.cargarHistorial();
        this.cargarResumenDashboard();
        this.cargarMontos();
      },
      error: (error) => {
        const mensaje = error.error?.detail || error.message || 'No se pudo actualizar';
        alert(mensaje);
      }
    });
  }

  get servicioSeleccionado(): SolicitudActiva | undefined {
    return this.serviciosActivos.find(s => s.id === this.servicioSeleccionadoId);
  }

  cargarResumenDashboard(): void {
  this.panelTallerService.obtenerResumenDashboard(this.taller.email).subscribe({
    next: (resp: DashboardTallerResumen) => {
      this.dashboardCards = resp.cards;
      this.serviciosChartData = { 
        labels: resp.charts.servicios.labels, 
        datasets: [{ label: 'Servicios', data: resp.charts.servicios.data }] 
      };
      this.completadosChartData = { 
        labels: resp.charts.completados.labels, 
        datasets: [{ label: 'Completados', data: resp.charts.completados.data }] 
      };
      this.activosChartData = { 
        labels: resp.charts.activos.labels, 
        datasets: [{ label: 'Activos', data: resp.charts.activos.data, tension: 0.35, fill: false }] 
      };
      this.ingresosChartData = { 
        labels: resp.charts.ingresos.labels, 
        datasets: [{ label: 'Ingresos', data: resp.charts.ingresos.data }] 
      };
    },
    error: (error) => console.error('Error:', error)
  });
}

  cargarHistorial(): void {
    this.panelTallerService.obtenerHistorial(this.taller.email).subscribe({
      next: (resp: HistorialTallerItem[]) => {
        this.historial = resp;
      },
      error: (error) => {
        this.historial = [];
      }
    });
  }

  generarNotificacionesDesdeSolicitudes(solicitudes: SolicitudActiva[]): NotificacionTaller[] {
    return solicitudes.slice(0, 5).map((s) => ({
      titulo: 'Nueva solicitud asignada',
      detalle: `${s.servicio} - ${s.cliente}`,
      tiempo: this.calcularTiempoRelativo(s.fecha),
      fechaBase: s.fecha
    }));
  }

  convertirAFecha(fecha: string): Date {
    if (!fecha) return new Date();
    const fechaNormalizada = fecha.includes('T') ? fecha : fecha.includes(' ') ? fecha.replace(' ', 'T') : `${fecha}T00:00:00`;
    const fechaConvertida = new Date(fechaNormalizada);
    return isNaN(fechaConvertida.getTime()) ? new Date() : fechaConvertida;
  }

  calcularTiempoRelativo(fecha: string): string {
    if (!fecha) return 'Recién';
    const diff = new Date().getTime() - this.convertirAFecha(fecha).getTime();
    const minutos = Math.floor(diff / 60000);
    if (minutos < 1) return 'Hace 1 min';
    if (minutos < 60) return `Hace ${minutos} min`;
    const horas = Math.floor(minutos / 60);
    if (horas < 24) return `Hace ${horas} h`;
    const dias = Math.floor(horas / 24);
    return `Hace ${dias} día${dias > 1 ? 's' : ''}`;
  }

  toggleEstadoTaller(): void {
    this.estadoTaller = this.estadoTaller === 'Activo' ? 'Inactivo' : 'Activo';
  }

  verTodasNotificaciones(): void {
    alert(`Total notificaciones: ${this.notificaciones.length}\n\n${this.notificaciones.map(n => `${n.titulo}: ${n.detalle}`).join('\n')}`);
  }

  getPrioridadClase(prioridad: string): string {
    switch (prioridad) {
      case 'Alta': return 'prioridad alta';
      case 'Media': return 'prioridad media';
      case 'Baja': return 'prioridad baja';
      default: return 'prioridad';
    }
  }

  get solicitudesFiltradas() {
    return this.solicitudesActivas.filter((s) => {
      const busqueda = this.filtros.busqueda.toLowerCase();
      const coincideBusqueda = !busqueda || s.codigo.toLowerCase().includes(busqueda) || s.servicio.toLowerCase().includes(busqueda) || s.cliente.toLowerCase().includes(busqueda);
      const coincideEstado = !this.filtros.estado || s.estado === this.filtros.estado;
      const coincidePrioridad = !this.filtros.prioridad || s.prioridad === this.filtros.prioridad;
      const coincideCliente = !this.filtros.cliente || s.cliente.toLowerCase().includes(this.filtros.cliente.toLowerCase());
      const coincideFecha = !this.filtros.fecha || s.fecha.startsWith(this.filtros.fecha);
      return coincideBusqueda && coincideEstado && coincidePrioridad && coincideCliente && coincideFecha;
    });
  }

  get historialFiltrado() {
    return this.historial.filter((h) => {
      const busqueda = this.filtrosHistorial.busqueda.toLowerCase();
      const coincideBusqueda = !busqueda || h.servicio.toLowerCase().includes(busqueda) || h.cliente.toLowerCase().includes(busqueda);
      const coincideEstado = !this.filtrosHistorial.estado || h.estado === this.filtrosHistorial.estado;
      const coincideCliente = !this.filtrosHistorial.cliente || h.cliente.toLowerCase().includes(this.filtrosHistorial.cliente.toLowerCase());
      const coincideFecha = !this.filtrosHistorial.fecha || h.fecha.startsWith(this.filtrosHistorial.fecha);
      return coincideBusqueda && coincideEstado && coincideCliente && coincideFecha;
    });
  }

  limpiarFiltros(): void {
    this.filtros = { busqueda: '', estado: '', prioridad: '', cliente: '', fecha: '' };
  }

  limpiarFiltrosHistorial(): void {
    this.filtrosHistorial = { busqueda: '', estado: '', cliente: '', fecha: '' };
  }

  setMenu(menu: string): void {
    this.selectedMenu = menu;
  }

  mostrarPerfil(): void {
    this.selectedMenu = 'perfil';
  }

 // En abrirModalAsignacion
abrirModalAsignacion(): void {
  this.mostrarModalAsignacion = true;
  this.solicitudSeleccionadaId = null;
  this.tecnicoSeleccionadoId = null;
  this.cargarTecnicosDisponibles(); // Usar el nuevo método
}

  cerrarModalAsignacion(): void {
    this.mostrarModalAsignacion = false;
    this.solicitudSeleccionadaId = null;
    this.tecnicoSeleccionadoId = null;
  }

 // Para cargar técnicos disponibles en el modal de asignación
cargarTecnicosDisponibles(): void {
  if (!this.tallerId) {
    console.log('❌ No hay tallerId');
    return;
  }
  console.log('🔧 Cargando técnicos disponibles para taller ID:', this.tallerId);
  
  this.cargandoTecnicos = true;
  this.panelTallerService.obtenerTecnicosPorTallerId(this.tallerId).subscribe({
    next: (resp: TecnicoTaller[]) => {
      console.log('✅ Técnicos disponibles:', resp);
      // Filtrar solo los activos/disponibles
      this.tecnicosDisponibles = resp.filter(t => t.estado?.toLowerCase() === 'activo' || t.estado?.toLowerCase() === 'disponible');
      this.cargandoTecnicos = false;
    },
    error: (error) => {
      console.error('❌ Error al cargar técnicos:', error);
      this.tecnicosDisponibles = [];
      this.cargandoTecnicos = false;
    }
  });
}

  confirmarAsignacionTecnico(): void {
    if (!this.solicitudSeleccionadaId) {
      alert('Debes seleccionar una solicitud.');
      return;
    }
    if (!this.tecnicoSeleccionadoId) {
      alert('Debes seleccionar un técnico.');
      return;
    }

    this.guardandoAsignacion = true;
    this.panelTallerService.asignarTecnico(this.solicitudSeleccionadaId, this.tecnicoSeleccionadoId).subscribe({
      next: (resp: AsignacionTecnicoResponse) => {
        alert(resp.message);
        this.guardandoAsignacion = false;
        this.cerrarModalAsignacion();
        this.cargarSolicitudesYNotificaciones();
        this.cargarServiciosActivos();
        this.cargarResumenDashboard();
        this.cargarHistorial();
      },
      error: (error) => {
        alert(error?.error?.detail || 'No se pudo asignar el técnico.');
        this.guardandoAsignacion = false;
      }
    });
  }

 // En abrirModalRegistroServicio
abrirModalRegistroServicio(): void {
  this.mostrarModalRegistroServicio = true;
  this.registroServicio = { incidente_id: null, tecnico_id: null, tiempo_estimado: null };
  this.cargarIncidentesDisponibles();
  this.cargarTecnicosDisponibles(); // Usar el nuevo método
}

  cerrarModalRegistroServicio(): void {
    this.mostrarModalRegistroServicio = false;
    this.registroServicio = { incidente_id: null, tecnico_id: null, tiempo_estimado: null };
  }

  cargarIncidentesDisponibles(): void {
    if (!this.taller.email) return;
    this.cargandoIncidentes = true;
    this.panelTallerService.obtenerIncidentesDisponibles(this.taller.email).subscribe({
      next: (resp: IncidenteDisponible[]) => {
        this.incidentesDisponibles = resp;
        this.cargandoIncidentes = false;
      },
      error: (error) => {
        this.incidentesDisponibles = [];
        this.cargandoIncidentes = false;
      }
    });
  }

  confirmarRegistroServicio(): void {
    if (!this.tallerId) {
      alert('No se encontró el id del taller logueado.');
      return;
    }
    if (!this.registroServicio.incidente_id) {
      alert('Debes seleccionar un incidente.');
      return;
    }

    const payload: RegistrarServicioPayload = {
      taller_id: this.tallerId,
      tecnico_id: null,
      incidente_id: this.registroServicio.incidente_id,
      estado: this.registroServicio.tecnico_id ? 'asignado' : 'pendiente',
      tiempo_estimado: this.registroServicio.tiempo_estimado,
      inicio: null,
      fin: null
    };

    this.guardandoServicio = true;
    this.panelTallerService.registrarServicio(payload).subscribe({
      next: () => {
        alert('Servicio registrado correctamente.');
        this.guardandoServicio = false;
        this.cerrarModalRegistroServicio();
        this.cargarSolicitudesYNotificaciones();
        this.cargarResumenDashboard();
        this.cargarHistorial();
      },
      error: (error) => {
        alert(error?.error?.detail || 'No se pudo registrar el servicio.');
        this.guardandoServicio = false;
      }
    });
  }

  aceptarSolicitud(solicitud: SolicitudActiva): void {
    if (!confirm(`¿Aceptar la solicitud ${solicitud.codigo}?`)) return;
    this.panelTallerService.aceptarServicioBackend(solicitud.id, this.taller.email).subscribe({
      next: (resp) => {
        alert(`✅ ${resp.message}`);
        this.cargarSolicitudesYNotificaciones();
        this.cargarServiciosActivos();
        this.cargarResumenDashboard();
      },
      error: (error) => {
        alert(error.error?.detail || 'No se pudo aceptar la solicitud');
      }
    });
  }

  asignarTecnico(solicitud: SolicitudActiva): void {
    this.abrirModalAsignacion();
    this.solicitudSeleccionadaId = solicitud.id;
  }

  cerrarServicio(solicitud: SolicitudActiva): void {
    alert(`La acción "Cerrar servicio" aún no está conectada al backend.`);
  }

  getEstadoClase(estado: string): string {
    switch (estado) {
      case 'Pendiente': return 'estado pendiente';
      case 'Aceptada': return 'estado aceptada';
      case 'Asignado': return 'estado asignado';
      case 'En proceso': return 'estado proceso';
      case 'Finalizado': return 'estado finalizado';
      case 'Cerrado': return 'estado cerrado';
      default: return 'estado';
    }
  }

  // ==================== MÉTODOS PARA TÉCNICOS ====================
 registrarTecnico(): void {
  if (!this.nombreTecnico) {
    alert('Ingresa el nombre del técnico');
    return;
  }

  this.registrando = true;

  this.panelTallerService.registrarTecnico({
    taller_id: this.tallerId,  // ← Usar ID, no email
    nombre: this.nombreTecnico,
    estado: 'activo'
  }).subscribe({
    next: () => {
      alert('✅ Técnico registrado');
      this.nombreTecnico = '';
      this.cargarTecnicos();
      this.registrando = false;
    },
    error: (error) => {
      alert(error.error?.detail || '❌ Error al registrar');
      this.registrando = false;
    }
  });
}

 // Cargar técnicos para la lista
cargarTecnicos(): void {
  if (!this.tallerId) {
    console.log('❌ No hay tallerId');
    return;
  }
  console.log('🔧 Cargando técnicos para taller ID:', this.tallerId);
  
  this.panelTallerService.obtenerTecnicosPorTallerId(this.tallerId).subscribe({
    next: (resp) => {
      console.log('✅ Técnicos recibidos:', resp);
      this.tecnicos = resp;
    },
    error: (error) => {
      console.error('❌ Error:', error);
      this.tecnicos = [];
    }
  });
}

  cambiarEstadoTecnico(id: number, estadoActual: string): void {
    const nuevoEstado = estadoActual === 'activo' ? 'inactivo' : 'activo';
    const mensaje = nuevoEstado === 'activo' ? 'activar' : 'desactivar';
    
    if (confirm(`¿${mensaje} este técnico?`)) {
      this.panelTallerService.cambiarEstadoTecnico(id, nuevoEstado).subscribe({
        next: () => {
          alert(`✅ Técnico ${mensaje}do`);
          this.cargarTecnicos();
        },
        error: () => alert('❌ Error al cambiar estado')
      });
    }
  }

  cambiarEstado(id: number, estadoActual: string): void {
  let nuevoEstado = '';
  let mensaje = '';
  
  if (estadoActual === 'disponible' || estadoActual === 'activo') {
    nuevoEstado = 'ocupado';
    mensaje = 'ocupar';
  } else {
    nuevoEstado = 'disponible';
    mensaje = 'disponibilizar';
  }
  
  if (confirm(`¿${mensaje} este técnico?`)) {
    this.panelTallerService.cambiarEstadoTecnico(id, nuevoEstado).subscribe({
      next: () => {
        alert(`✅ Técnico ${mensaje}do`);
        this.cargarTecnicos();
      },
      error: () => alert('❌ Error al cambiar estado')
    });
  }
}

  eliminarTecnico(id: number): void {
    if (confirm('¿Eliminar este técnico?')) {
      this.panelTallerService.eliminarTecnico(id).subscribe({
        next: () => {
          alert('✅ Técnico eliminado');
          this.cargarTecnicos();
        },
        error: () => alert('❌ Error al eliminar')
      });
    }
  }

  toggleNotificaciones(): void {
    this.mostrarNotificaciones = !this.mostrarNotificaciones;
  }

  getMapUrl(ubicacion: string): string {
  const direccion = encodeURIComponent(ubicacion);
  return `https://www.google.com/maps/embed/v1/place?key=AIzaSyCpTnVytPXeGEOzbyAAMPr9EyV50HEv7ow&q=${direccion}`;
 }

 // Verificar si es un link de Google Maps
esLinkDeGoogleMaps(ubicacion: string): boolean {
  if (!ubicacion) return false;
  return ubicacion.includes('maps.app.goo.gl') || 
         ubicacion.includes('google.com/maps');
}

// Convertir el link de Google Maps a un embed URL
convertirLinkAMapa(link: string): string {
  // Si ya es un embed, devolverlo directamente
  if (link.includes('embed')) return link;
  
  // Extraer el ID del link o usar directamente
  // Por ahora usamos un enfoque simple: mostrar el link en un iframe de Google Maps
  return `https://www.google.com/maps/embed/v1/place?key=AIzaSyCpTnVytPXeGEOzbyAAMPr9EyV50HEv7ow&q=${encodeURIComponent(link)}`;
}

  cerrarSesion(): void {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.removeItem('taller_logueado');
    }
    this.router.navigate(['/login']);
  }
}