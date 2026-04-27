import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface SolicitudActiva {
  id: number;
  codigo: string;
  servicio: string;
  cliente: string;
  ubicacion: string;
  estado: string;
  prioridad: string;
  tecnico: string;
  telefonoTecnico: string;
  fecha: string;
  vehiculo: string;
}

export interface DashboardTallerResumen {
  cards: {
    servicios_asignados: number;
    servicios_completados_mes: number;
    servicios_activos: number;
    ingresos_mes: number;
  };
  charts: {
    servicios: { labels: string[]; data: number[] };
    completados: { labels: string[]; data: number[] };
    activos: { labels: string[]; data: number[] };
    ingresos: { labels: string[]; data: number[] };
  };
}

export interface HistorialTallerItem {
  id: number;
  servicio: string;
  cliente: string;
  estado: string;
  monto: number;
  fecha: string;
}

export interface TecnicoTaller {
  id: number;
  nombre: string;
  estado: string;
}

export interface AsignacionTecnicoResponse {
  message: string;
  servicio_id: number;
  tecnico_id: number;
  tecnico_nombre: string;
  estado: string;
}

export interface IncidenteDisponible {
  id: number;
  cliente: string;
  servicio: string;
  ubicacion: string;
  prioridad: string;
  fecha: string;
  vehiculo: string;
}

export interface RegistrarServicioPayload {
  taller_id: number;
  tecnico_id: number | null;
  incidente_id: number;
  estado: string;
  tiempo_estimado: number | null;
  inicio: string | null;
  fin: string | null;
}

@Injectable({
  providedIn: 'root'
})
export class PanelTallerService {
  private http = inject(HttpClient);
  private readonly baseUrl = 'http://18.223.2.124:8000/api';

  obtenerSolicitudesActivas(tallerEmail: string): Observable<SolicitudActiva[]> {
    return this.http.get<SolicitudActiva[]>(`${this.baseUrl}/servicios/activas?taller_email=${encodeURIComponent(tallerEmail)}`);
  }

  obtenerResumenDashboard(tallerEmail: string): Observable<DashboardTallerResumen> {
    return this.http.get<DashboardTallerResumen>(`${this.baseUrl}/dashboard/taller/resumen?taller_email=${encodeURIComponent(tallerEmail)}`);
  }

  obtenerHistorial(tallerEmail: string): Observable<HistorialTallerItem[]> {
    return this.http.get<HistorialTallerItem[]>(`${this.baseUrl}/servicios/historial?taller_email=${encodeURIComponent(tallerEmail)}`);
  }

  /*
  obtenerTecnicosPorTaller(tallerEmail: string): Observable<TecnicoTaller[]> {
    return this.http.get<TecnicoTaller[]>(`${this.baseUrl}/tecnicos/por-taller?taller_email=${encodeURIComponent(tallerEmail)}`);
  }*/

// Cambiar de taller_email a taller_id
obtenerTecnicosPorTallerId(tallerId: number | null): Observable<any[]> {
  return this.http.get<any[]>(`${this.baseUrl}/tecnicos/por-taller?taller_id=${tallerId}`);
}

// También el método para asignar técnicos (si usas el mismo)
obtenerTecnicosDisponibles(tallerId: number | null): Observable<TecnicoTaller[]> {
  return this.http.get<TecnicoTaller[]>(`${this.baseUrl}/tecnicos/disponibles?taller_id=${tallerId}`);
}


  asignarTecnico(servicioId: number, tecnicoId: number): Observable<AsignacionTecnicoResponse> {
    return this.http.put<AsignacionTecnicoResponse>(
      `${this.baseUrl}/servicios/${servicioId}/asignar-tecnico?tecnico_id=${tecnicoId}`,
      {}
    );
  }

  obtenerIncidentesDisponibles(tallerEmail: string): Observable<IncidenteDisponible[]> {
    return this.http.get<IncidenteDisponible[]>(`${this.baseUrl}/incidentes/disponibles?taller_email=${encodeURIComponent(tallerEmail)}`);
  }

  actualizarEstadoServicio(servicioId: number, nuevoEstado: string): Observable<any> {
  console.log('📡 Enviando petición:', { servicioId, nuevoEstado });
  return this.http.put<any>(`${this.baseUrl}/servicios/${servicioId}/actualizar-estado`, {
    nuevo_estado: nuevoEstado
   });
  }

  aceptarServicioBackend(servicioId: number, tallerEmail: string): Observable<any> {
  return this.http.put<any>(`${this.baseUrl}/servicios/${servicioId}/aceptar-servicio?taller_email=${encodeURIComponent(tallerEmail)}`, {});
 }

 obtenerMontosTaller(tallerEmail: string): Observable<any> {
  return this.http.get<any>(`${this.baseUrl}/taller/montos?taller_email=${encodeURIComponent(tallerEmail)}`);
}

obtenerBilleteraTaller(tallerEmail: string): Observable<any> {
  return this.http.get<any>(`${this.baseUrl}/taller/billetera?taller_email=${encodeURIComponent(tallerEmail)}`);
}

recargarSaldo(tallerEmail: string, monto: number, recurrente: boolean): Observable<any> {
  return this.http.post<any>(`${this.baseUrl}/taller/recargar`, {
    taller_email: tallerEmail,
    monto: monto,
    recurrente: recurrente
  });
}

obtenerSaldoTaller(tallerEmail: string): Observable<any> {
  return this.http.get<any>(`${this.baseUrl}/taller/montos/saldo?taller_email=${encodeURIComponent(tallerEmail)}`);
}

actualizarPerfilTaller(tallerEmail: string, datos: any): Observable<any> {
  return this.http.put<any>(`${this.baseUrl}/perfil/taller/actualizar?taller_email=${encodeURIComponent(tallerEmail)}`, datos);
}

obtenerNotificacionesTaller(tallerEmail: string): Observable<any[]> {
  return this.http.get<any[]>(`${this.baseUrl}/taller/notificaciones?taller_email=${encodeURIComponent(tallerEmail)}`);
}

// Registrar técnico (solo nombre, el estado se pone por defecto)
/*registrarTecnico(tallerId: number, nombre: string): Observable<any> {
  return this.http.post<any>(`${this.baseUrl}/tecnicos/?taller_id=${tallerId}&nombre=${nombre}&estado=activo`, {});
}*/

registrarTecnico(data: any): Observable<any> {
  return this.http.post(`${this.baseUrl}/tecnicos/`, data);
}



// Cambiar estado
cambiarEstadoTecnico(id: number, estado: string): Observable<any> {
  return this.http.put(`${this.baseUrl}/tecnicos/${id}/estado?estado=${estado}`, {});
}

actualizarEstadoTecnico(id: number, estado: string): Observable<any> {
  return this.http.put<any>(`${this.baseUrl}/tecnicos/${id}/estado?estado=${estado}`, {});
}

actualizarTecnico(id: number, data: any): Observable<any> {
  return this.http.put<any>(`${this.baseUrl}/tecnicos/${id}`, data);
}

eliminarTecnico(id: number): Observable<any> {
  return this.http.delete(`${this.baseUrl}/tecnicos/${id}`);
}

  registrarServicio(payload: RegistrarServicioPayload): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/servicios/`, payload);
  }
}