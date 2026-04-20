import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface SolicitudActiva {
  id?: number;
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

@Injectable({
  providedIn: 'root'
})
export class PanelTallerService {
  private http = inject(HttpClient);
  private readonly baseUrl = 'http://18.223.2.124:8000/api';

  obtenerSolicitudesActivas(tallerEmail: string): Observable<SolicitudActiva[]> {
    return this.http.get<SolicitudActiva[]>(
      `${this.baseUrl}/servicios/activas?taller_email=${encodeURIComponent(tallerEmail)}`
    );
  }

  obtenerResumenDashboard(tallerEmail: string): Observable<DashboardTallerResumen> {
    return this.http.get<DashboardTallerResumen>(
      `${this.baseUrl}/dashboard/taller/resumen?taller_email=${encodeURIComponent(tallerEmail)}`
    );
  }
}