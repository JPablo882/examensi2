import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface DashboardAdminResumen {
  cards: {
    usuarios_totales: number;
    talleres_registrados: number;
    solicitudes_activas: number;
    ingresos_mes: number;
  };
  charts: {
    usuarios: { labels: string[]; data: number[] };
    talleres: { labels: string[]; data: number[] };
    solicitudes: { labels: string[]; data: number[] };
    ingresos: { labels: string[]; data: number[] };
  };
}

export interface SolicitudAdminReciente {
  id: number;
  servicio: string;
  usuario: string;
  taller: string;
  estado: string;
  fecha: string;
}

export interface UsuarioAdmin {
  id: number;
  inicial: string;
  nombre: string;
  rol: string;
  estado: string;
  email: string;
  telefono: string;
  ultimoAcceso: string;
  creado: string;
}

@Injectable({
  providedIn: 'root'
})
export class PanelAdminService {
  private http = inject(HttpClient);
  private readonly baseUrl = 'http://18.223.2.124:8000/api';

  obtenerResumenDashboard(): Observable<DashboardAdminResumen> {
    return this.http.get<DashboardAdminResumen>(
      `${this.baseUrl}/dashboard/admin/resumen`
    );
  }

  obtenerSolicitudesRecientes(): Observable<SolicitudAdminReciente[]> {
    return this.http.get<SolicitudAdminReciente[]>(
      `${this.baseUrl}/admin/solicitudes/recientes`
    );
  }

  obtenerPerfilAdmin(adminEmail: string): Observable<any> {
  return this.http.get<any>(`${this.baseUrl}/admin/perfil?admin_email=${encodeURIComponent(adminEmail)}`);
}

actualizarPerfilAdmin(datos: any): Observable<any> {
  const adminEmail = 'dbanegas205@gmail.com';
  return this.http.put<any>(`${this.baseUrl}/admin/perfil/actualizar?admin_email=${encodeURIComponent(adminEmail)}`, datos);
}

obtenerDetalleSolicitud(id: number): Observable<any> {
  return this.http.get<any>(`${this.baseUrl}/admin/solicitudes/${id}`);
}

consultarAsistente(mensaje: string): Observable<any> {
  console.log('📡 Enviando consulta:', mensaje);
  // 🔥 USA GET (coincide con tu backend)
  return this.http.get<any>(`${this.baseUrl}/asistente/consultar?mensaje=${encodeURIComponent(mensaje)}`);
}

obtenerReportePagos(): Observable<any[]> {
  return this.http.get<any[]>(`${this.baseUrl}/reportes/pagos`);
}

// Obtener reporte de servicios desde FastAPI
obtenerReporteServicios(): Observable<any[]> {
  // ✅ Usa la misma base URL que pagos
  return this.http.get<any[]>(`${this.baseUrl}/reportes/servicios`);
}

// Opcional: Obtener estadísticas de servicios
obtenerEstadisticasServicios(): Observable<any> {
  return this.http.get<any>(`${this.baseUrl}/reportes/servicios/estadisticas`);
}

// Opcional: Obtener detalle de un servicio
obtenerDetalleServicio(servicioId: number): Observable<any> {
  return this.http.get<any>(`${this.baseUrl}/reportes/servicios/${servicioId}`);
}

  obtenerUsuariosSistema(): Observable<UsuarioAdmin[]> {
    return this.http.get<UsuarioAdmin[]>(
      `${this.baseUrl}/admin/usuarios`
    );
  }
}