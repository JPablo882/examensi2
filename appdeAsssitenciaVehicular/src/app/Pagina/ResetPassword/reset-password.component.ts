import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-reset-password',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './reset-password.component.html',
  styleUrl: './reset-password.component.css'
})
export class ResetPasswordComponent {
  token: string = '';
  nuevaPassword: string = '';
  confirmarPassword: string = '';
  cargando: boolean = false;
  tokenValido: boolean = false;
  verificado: boolean = false;
  error: string = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private http: HttpClient
  ) {
    this.route.queryParams.subscribe(params => {
      this.token = params['token'];
      if (this.token) {
        this.verificarToken();
      } else {
        this.error = 'Token no válido';
        this.verificado = true;
      }
    });
  }

  verificarToken(): void {
    this.http.get(`http://localhost:8000/api/password/verificar-token?token=${this.token}`)
      .subscribe({
        next: () => {
          this.tokenValido = true;
          this.verificado = true;
        },
        error: (err) => {
          this.error = err.error?.detail || 'El enlace ha expirado o es inválido';
          this.tokenValido = false;
          this.verificado = true;
        }
      });
  }

  resetearPassword(): void {
    if (!this.nuevaPassword) {
      alert('Ingresa una nueva contraseña');
      return;
    }

    if (this.nuevaPassword.length < 6) {
      alert('La contraseña debe tener al menos 6 caracteres');
      return;
    }

    if (this.nuevaPassword !== this.confirmarPassword) {
      alert('Las contraseñas no coinciden');
      return;
    }

    this.cargando = true;

    this.http.post('http://localhost:8000/api/password/reset', {
      token: this.token,
      nueva_password: this.nuevaPassword
    }).subscribe({
      next: () => {
        alert('✅ Contraseña actualizada correctamente. Ahora puedes iniciar sesión.');
        this.router.navigate(['/login']);
      },
      error: (err) => {
        alert(err.error?.detail || 'Error al actualizar la contraseña');
        this.cargando = false;
      }
    });
  }
}