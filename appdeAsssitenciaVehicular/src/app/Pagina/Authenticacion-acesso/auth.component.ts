import { CommonModule, isPlatformBrowser } from '@angular/common';
import { Component, Inject, PLATFORM_ID, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-auth',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './auth.component.html',
  styleUrl: './auth.component.css'
})
export class AuthComponent {
  private authService = inject(AuthService);
  private router = inject(Router);

  constructor(@Inject(PLATFORM_ID) private platformId: Object) {}

  mode: 'login' | 'register' = 'login';

  loginData = {
    email: '',
    password: '',
    remember: false
  };

  registerData = {
    nombreCompleto: '',
    email: '',
    telefono: '',
    password: '',
    confirmPassword: '',
    aceptaTerminos: false,
    nombreTaller: '',
    direccion: '',
    ubicacion: '',
    emailTaller: ''
  };

  cambiarModo(mode: 'login' | 'register'): void {
    this.mode = mode;
  }

  iniciarSesion(): void {
    this.authService.login(
      this.loginData.email,
      this.loginData.password,
      'taller'
    ).subscribe({
      next: (resp) => {
        if (isPlatformBrowser(this.platformId)) {
          localStorage.setItem('taller_logueado', JSON.stringify(resp.user));
        }

        alert(`Bienvenido taller ${resp.user.nombre}`);
        this.router.navigate(['/panel-taller']);
      },
      error: (err) => {
        alert(err?.error?.detail || 'No se pudo iniciar sesión.');
      }
    });
  }

  registrarTaller(): void {
    if (this.registerData.password !== this.registerData.confirmPassword) {
      alert('Las contraseñas no coinciden');
      return;
    }

    if (!this.registerData.aceptaTerminos) {
      alert('Debes aceptar los términos y condiciones');
      return;
    }

    this.authService.registerTaller(this.registerData).subscribe({
      next: (resp) => {
        alert(resp?.message || 'Taller registrado correctamente.');

        this.loginData.email = this.registerData.email;
        this.loginData.password = this.registerData.password;

        this.registerData = {
          nombreCompleto: '',
          email: '',
          telefono: '',
          password: '',
          confirmPassword: '',
          aceptaTerminos: false,
          nombreTaller: '',
          direccion: '',
          ubicacion: '',
          emailTaller: ''
        };

        this.mode = 'login';
      },
      error: (err) => {
        alert(err?.error?.detail || 'No se pudo registrar el taller.');
      }
    });
  }
}