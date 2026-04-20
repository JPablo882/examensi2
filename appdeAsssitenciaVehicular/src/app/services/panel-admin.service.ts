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

  obtenerUsuariosSistema(): Observable<UsuarioAdmin[]> {
    return this.http.get<UsuarioAdmin[]>(
      `${this.baseUrl}/admin/usuarios`
    );
  }
}