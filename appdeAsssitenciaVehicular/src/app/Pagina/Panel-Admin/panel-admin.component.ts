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
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-panel-admin',
  standalone: true,
  imports: [CommonModule, FormsModule, BaseChartDirective],
  templateUrl: './panel-admin.component.html',
  styleUrl: './panel-admin.component.css'
})
export class PanelAdminComponent implements OnInit {
  private panelAdminService = inject(PanelAdminService);
  private http = inject(HttpClient);

  admin = {
    nombre: 'admin',
    email: 'admin@emergauto.com'
  };

  selectedMenu = 'dashboard';
  isBrowser = false;

  //variables para reportes pagos
  //Pagos
  reportePagos: any[]=[];
  cargandoReporte: boolean = false;
  modalReporteAbierto: boolean = false;
 // servicios
 reporteServicios: any[] = [];
 cargandoReporteServicios: boolean = false;
 modalServiciosAbierto: boolean = false;


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

  // Agrega estas variables
mostrarModalEditarPerfil: boolean = false;
guardandoPerfil: boolean = false;
perfilEditado = {
  nombre: '',
  apellidos: '',
  telefono: '',
  direccion: '',
  ciudad: ''
};

  mensajesSoporte = [
    {
      autor: 'ia',
      tipo: 'texto',
      contenido: 'Hola, soy el asistente del panel administrativo. Puedo ayudarte con solicitudes, alertas, usuarios y talleres.',
      hora: 'Ahora'
    }
  ];

// Variables
mostrarModalDetalle: boolean = false;
solicitudDetalle: any = null;

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
    this.cargarPerfilAdmin();
  }

   // Cargar reporte de pagos desde FastAPI
  cargarReportePagos(): void {
    this.cargandoReporte = true;
    this.panelAdminService.obtenerReportePagos().subscribe({
      next: (resp) => {
        this.reportePagos = resp;
        this.cargandoReporte = false;
        console.log('✅ Reporte de pagos:', this.reportePagos);
      },
      error: (error) => {
        console.error('❌ Error:', error);
        alert('Error al cargar el reporte de pagos');
        this.cargandoReporte = false;
      }
    });
  }

  // Exportar a PDF (imprimir)
  exportarPDF(): void {
    if (this.reportePagos.length === 0) {
      alert('⚠️ No hay datos para exportar');
      return;
    }
    const contenido = this.generarHTMLReporte();
    const ventana = window.open();
    ventana?.document.write(contenido);
    ventana?.document.close();
    ventana?.print();
  }

  // Exportar a Excel (CSV)
  exportarExcel(): void {
    if (this.reportePagos.length === 0) {
      alert('⚠️ No hay datos para exportar');
      return;
    }

    let csv = "ID,Servicio ID,Monto,Comisión,Estado,Fecha\n";
    
    this.reportePagos.forEach(p => {
      csv += `${p.id},${p.servicio_id},${p.monto},${p.comision},${p.estado},${p.fecha}\n`;
    });
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `reporte_pagos_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    alert('✅ Reporte exportado a Excel');
  }

  // Exportar a HTML
  exportarHTML(): void {
    if (this.reportePagos.length === 0) {
      alert('⚠️ No hay datos para exportar');
      return;
    }

    const contenido = this.generarHTMLReporte();
    const blob = new Blob([contenido], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `reporte_pagos_${new Date().toISOString().split('T')[0]}.html`;
    a.click();
    URL.revokeObjectURL(url);
    alert('✅ Reporte exportado a HTML');
  }


  // Generar HTML para reporte - VERSIÓN CORREGIDA
generarHTMLReporte(): string {
  // Crear las filas de la tabla como string
  const filasTabla = this.reportePagos.map(p => `
    <tr>
      <td>${p.id}</td>
      <td>${p.servicio_id}</td>
      <td>Bs ${p.monto}</td>
      <td>Bs ${p.comision}</td>
      <td>${p.estado}</td>
      <td>${p.fecha}</td>
    </tr>
  `).join('');
  
  return `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <title>Reporte de Pagos - EmergAuto</title>
      <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #ff6200; text-align: center; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
        th { background: #ff6200; color: white; }
        .footer { text-align: center; margin-top: 30px; font-size: 12px; color: #666; }
        .total { margin-top: 20px; font-weight: bold; text-align: right; }
      </style>
    </head>
    <body>
      <h1>📊 Reporte de Pagos - EmergAuto</h1>
      <p>Fecha de generación: ${new Date().toLocaleString()}</p>
      <p>Total de pagos: ${this.reportePagos.length}</p>
      
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Servicio ID</th>
            <th>Monto (Bs)</th>
            <th>Comisión (Bs)</th>
            <th>Estado</th>
            <th>Fecha</th>
          </tr>
        </thead>
        <tbody>
          ${filasTabla}
        </tbody>
      </table>
      
      <div class="total">
        <p>💰 Total recaudado: Bs ${this.calcularTotal()}</p>
      </div>
      
      <div class="footer">
        <p>EmergAuto - Sistema de Asistencia Vehicular</p>
        <p>© ${new Date().getFullYear()} - Todos los derechos reservados</p>
      </div>
    </body>
    </html>
  `;
}

 
  // Calcular total recaudado
calcularTotal(): number {
  return this.reportePagos.reduce((total, p) => total + (p.monto || 0), 0);
}

// Abrir modal de reporte
abrirModalReporte(): void {
  this.modalReporteAbierto = true;
  // Opcional: cargar datos automáticamente al abrir
  // this.cargarReportePagos();
}



// Cerrar modal
cerrarModalReporte(): void {
  this.modalReporteAbierto = false;
}

// Para otros reportes
abrirModalServicios(): void {
  // Similar pero para servicios
  this.modalServiciosAbierto = true;
  // this.cargarReporteServicios();
}

// Cerrar modal de servicios
cerrarModalServicios(): void {
  this.modalServiciosAbierto = false;
}

// Cargar reporte de servicios desde FastAPI
cargarReporteServicios(): void {
  this.cargandoReporteServicios = true;
  this.panelAdminService.obtenerReporteServicios().subscribe({
    next: (resp) => {
      this.reporteServicios = resp;
      this.cargandoReporteServicios = false;
      console.log('✅ Reporte de servicios:', this.reporteServicios);
    },
    error: (error) => {
      console.error('❌ Error:', error);
      alert('Error al cargar el reporte de servicios');
      this.cargandoReporteServicios = false;
    }
  });
}

// Exportar Servicios a PDF
exportarServiciosPDF(): void {
  if (this.reporteServicios.length === 0) {
    alert('⚠️ No hay datos para exportar');
    return;
  }
  const contenido = this.generarHTMLReporteServicios();
  const ventana = window.open();
  ventana?.document.write(contenido);
  ventana?.document.close();
  ventana?.print();
}

// Exportar Servicios a Excel (CSV)
exportarServiciosExcel(): void {
  if (this.reporteServicios.length === 0) {
    alert('⚠️ No hay datos para exportar');
    return;
  }

  let csv = "ID,Taller ID,Incidente ID,Estado,Tiempo Estimado,Inicio,Fin\n";
  
  this.reporteServicios.forEach(s => {
    csv += `${s.id},${s.taller_id},${s.incidente_id},${s.estado},${s.tiempo_estimado},${s.inicio},${s.fin}\n`;
  });
  
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `reporte_servicios_${new Date().toISOString().split('T')[0]}.csv`;
  a.click();
  URL.revokeObjectURL(url);
  alert('✅ Reporte de servicios exportado a Excel');
}

// Exportar Servicios a HTML
exportarServiciosHTML(): void {
  if (this.reporteServicios.length === 0) {
    alert('⚠️ No hay datos para exportar');
    return;
  }

  const contenido = this.generarHTMLReporteServicios();
  const blob = new Blob([contenido], { type: 'text/html' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `reporte_servicios_${new Date().toISOString().split('T')[0]}.html`;
  a.click();
  URL.revokeObjectURL(url);
  alert('✅ Reporte de servicios exportado a HTML');
}

// Generar HTML para reporte de servicios
generarHTMLReporteServicios(): string {
  const filasTabla = this.reporteServicios.map(s => `
    <tr>
      <td>${s.id}</td>
      <td>${s.taller_id || '-'}</td>
      <td>${s.incidente_id || '-'}</td>
      <td>${s.estado || '-'}</td>
      <td>${s.tiempo_estimado || '-'} min</td>
      <td>${s.inicio || '-'}</td>
      <td>${s.fin || '-'}</td>
    </tr>
  `).join('');
  
  return `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <title>Reporte de Servicios - EmergAuto</title>
      <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #ff6200; text-align: center; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
        th { background: #ff6200; color: white; }
        .footer { text-align: center; margin-top: 30px; font-size: 12px; color: #666; }
        .total { margin-top: 20px; font-weight: bold; text-align: right; }
        .estado-pendiente { color: #ffc107; }
        .estado-en-curso { color: #17a2b8; }
        .estado-completado { color: #28a745; }
      </style>
    </head>
    <body>
      <h1>🔧 Reporte de Servicios - EmergAuto</h1>
      <p>Fecha de generación: ${new Date().toLocaleString()}</p>
      <p>Total de servicios: ${this.reporteServicios.length}</p>
      
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Taller ID</th>
            <th>Incidente ID</th>
            <th>Estado</th>
            <th>Tiempo Estimado</th>
            <th>Inicio</th>
            <th>Fin</th>
          </tr>
        </thead>
        <tbody>
          ${filasTabla}
        </tbody>
      </table>
      
      <div class="total">
        <p>⏱️ Tiempo total estimado: ${this.calcularTiempoTotalServicios()} minutos</p>
        <p>✅ Servicios completados: ${this.contarServiciosPorEstado('completado')}</p>
        <p>🟡 Servicios pendientes: ${this.contarServiciosPorEstado('pendiente')}</p>
      </div>
      
      <div class="footer">
        <p>EmergAuto - Sistema de Asistencia Vehicular</p>
        <p>© ${new Date().getFullYear()} - Todos los derechos reservados</p>
      </div>
    </body>
    </html>
  `;
}

// Calcular tiempo total de servicios
calcularTiempoTotalServicios(): number {
  return this.reporteServicios.reduce((total, s) => total + (s.tiempo_estimado || 0), 0);
}

// Contar servicios por estado
contarServiciosPorEstado(estado: string): number {
  return this.reporteServicios.filter(s => s.estado?.toLowerCase() === estado.toLowerCase()).length;
}

// Formatear fecha para mostrar
formatearFecha(fecha: string): string {
  if (!fecha) return '-';
  return new Date(fecha).toLocaleString();
}



// Cargar perfil
cargarPerfilAdmin(): void {
  this.panelAdminService.obtenerPerfilAdmin('dbanegas205@gmail.com').subscribe({
    next: (resp) => {
      this.adminPerfil = {
        nombre: resp.nombre,
        apellidos: resp.apellidos || '',
        email: resp.email,
        telefono: resp.telefono || '',
        direccion: resp.direccion || 'Santa Cruz, Bolivia',
        ciudad: resp.ciudad || 'Santa Cruz',
        cargo: 'Administrador'
      };
      this.admin.nombre = resp.nombre;
      this.admin.email = resp.email;
    },
    error: (error) => console.error('Error:', error)
  });
}

cerrarModalEditarPerfil(): void {
  this.mostrarModalEditarPerfil = false;
  this.perfilEditado = { nombre: '', apellidos: '', telefono: '', direccion: '', ciudad: '' };
  this.guardandoPerfil = false;
}

guardarCambiosPerfil(): void {
  this.guardandoPerfil = true;
  
  const datos: any = {};
  if (this.perfilEditado.nombre) datos.nombre = this.perfilEditado.nombre;
  if (this.perfilEditado.apellidos) datos.apellidos = this.perfilEditado.apellidos;
  if (this.perfilEditado.telefono) datos.telefono = this.perfilEditado.telefono;
  if (this.perfilEditado.direccion) datos.direccion = this.perfilEditado.direccion;
  if (this.perfilEditado.ciudad) datos.ciudad = this.perfilEditado.ciudad;
  
  if (Object.keys(datos).length === 0) {
    alert('No se ingresaron cambios');
    this.guardandoPerfil = false;
    this.cerrarModalEditarPerfil();
    return;
  }
  
  this.panelAdminService.actualizarPerfilAdmin(datos).subscribe({
    next: (resp) => {
      alert('✅ Perfil actualizado correctamente');
      this.cargarPerfilAdmin();
      this.guardandoPerfil = false;
      this.cerrarModalEditarPerfil();
    },
    error: (error) => {
      alert('❌ Error al actualizar');
      this.guardandoPerfil = false;
    }
  });
}

// Agrega este método (lo tienes comentado o no está)
editarPerfil(): void {
  console.log('Editar perfil clickeado');
  this.perfilEditado = { nombre: '', apellidos: '', telefono: '', direccion: '', ciudad: '' };
  this.mostrarModalEditarPerfil = true;
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

  /*
  verDetalle(solicitud: SolicitudAdminReciente): void {
    alert(`Viendo detalle de: ${solicitud.servicio}`);
  }*/

  verDetalle(solicitud: SolicitudAdminReciente): void {
  this.panelAdminService.obtenerDetalleSolicitud(solicitud.id).subscribe({
    next: (resp) => {
      this.solicitudDetalle = resp;
      this.mostrarModalDetalle = true;
    },
    error: (error) => {
      console.error('Error:', error);
      alert('No se pudo cargar el detalle');
    }
  });
 }

// Cerrar modal
cerrarModalDetalle(): void {
  this.mostrarModalDetalle = false;
  this.solicitudDetalle = null;
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

  // Mensaje del admin
  this.mensajesSoporte.push({
    autor: 'admin',
    tipo: 'texto',
    contenido: texto,
    hora: 'Ahora'
  });

  this.mensajeSoporte = '';

  // 🔥 LLAMAR AL BACKEND CORRECTAMENTE
  this.panelAdminService.consultarAsistente(texto).subscribe({
    next: (resp) => {
      console.log('Respuesta del backend:', resp);
      this.mensajesSoporte.push({
        autor: 'ia',
        tipo: 'texto',
        contenido: resp.respuesta,  // ← Asegura que sea resp.respuesta
        hora: 'Ahora'
      });
    },
    error: (error) => {
      console.error('Error:', error);
      this.mensajesSoporte.push({
        autor: 'ia',
        tipo: 'texto',
        contenido: 'Lo siento, no pude procesar tu consulta en este momento.',
        hora: 'Ahora'
      });
    }
  });
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