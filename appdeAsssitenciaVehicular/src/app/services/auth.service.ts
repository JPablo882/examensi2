import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface LoginUser {
  id: number;
  nombre: string;
  email: string;
  telefono: string | null;
  rol: string;
}

export interface LoginResponse {
  message: string;
  user: LoginUser;
}

export interface RegisterTallerPayload {
  nombreCompleto: string;
  email: string;
  telefono: string;
  password: string;
  confirmPassword: string;
  aceptaTerminos: boolean;
  nombreTaller: string;
  direccion: string;
  ubicacion: string;
  emailTaller: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private http = inject(HttpClient);

  private readonly baseUrl = 'http://127.0.0.1:8000/api';
  private readonly loginUrl = `${this.baseUrl}/auth/login`;
  private readonly registerUrl = `${this.baseUrl}/auth/register-taller`;

  login(
    email: string,
    password: string,
    accessType: 'taller' | 'admin'
  ): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(this.loginUrl, {
      email,
      password,
      access_type: accessType
    });
  }

  registerTaller(payload: RegisterTallerPayload): Observable<any> {
    return this.http.post<any>(this.registerUrl, payload);
  }
}