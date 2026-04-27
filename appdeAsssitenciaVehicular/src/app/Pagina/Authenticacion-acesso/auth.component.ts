import { CommonModule, isPlatformBrowser } from '@angular/common';
import { Component, Inject, PLATFORM_ID, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { HttpClient } from '@angular/common/http';  // 🔥 IMPORTAR HTTPCLIENT

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
  private http = inject(HttpClient);  // 🔥 AGREGAR HTTPCLIENT

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

  // variable para el modal de recuperar contraseña
  mostrarModalRecuperar: boolean = false;
  recuperarEmail: string = '';
  enviando: boolean = false;

  //variable para bloqueo con temporizador 
  intentosFallidos: number = 0;
  bloqueado: boolean = false;
  tiempoRestante: number = 0;
  temporizador: any;

  

  cambiarModo(mode: 'login' | 'register'): void {
    this.mode = mode;
  }

  // Abrir modal de recuperar contraseña
  abrirModalRecuperar(event: Event): void {
    event.preventDefault();
    this.mostrarModalRecuperar = true;
    this.recuperarEmail = '';
  }

  // Cerrar modal de recuperar contraseña
  cerrarModalRecuperar(): void {
    this.mostrarModalRecuperar = false;
    this.recuperarEmail = '';
    this.enviando = false;
  }

  // 🔥 ENVIAR RECUPERACIÓN DE CONTRASEÑA - CONECTADO AL BACKEND
  enviarRecuperacion(): void {
    if (!this.recuperarEmail) {
      alert('Por favor, ingresa tu correo electrónico');
      return;
    }

    if (!this.recuperarEmail.includes('@') || !this.recuperarEmail.includes('.')) {
      alert('Por favor, ingresa un correo electrónico válido');
      return;
    }

    this.enviando = true;

    // Llamar al backend para enviar el correo de recuperación
    this.http.post('http://localhost:8000/api/password/recuperar', {
      email: this.recuperarEmail
    }).subscribe({
      next: (resp: any) => {
        alert(resp.message || '✅ Revisa tu correo para restablecer tu contraseña');
        this.enviando = false;
        this.cerrarModalRecuperar();
      },
      error: (err) => {
        console.error('Error:', err);
        alert(err.error?.detail || '❌ Error al enviar el correo. Intenta más tarde.');
        this.enviando = false;
      }
    });
  }
/*
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
  }*/

 iniciarSesion(): void {
    // Verificar si está bloqueado
    if (this.bloqueado && !this.esAdministrador()) {
      alert(`⏳ Cuenta bloqueada. Espera ${this.tiempoRestante} segundos.`);
      return;
    }

    this.authService.login(
      this.loginData.email,
      this.loginData.password,
      'taller'
    ).subscribe({
      next: (resp: any) => {
        // Login exitoso - resetear bloqueo
        this.resetearBloqueo();
        
        if (isPlatformBrowser(this.platformId)) {
          const tallerData = {
            id: resp.taller?.id,
            nombre: resp.taller?.nombre_taller || resp.user?.nombre,
            email: resp.taller?.email || resp.user?.email,
            telefono: resp.user?.telefono
          };
          console.log('💾 Guardando:', tallerData);
          localStorage.setItem('taller_logueado', JSON.stringify(tallerData));
        }

        alert(`Bienvenido ${resp.user.nombre}`);
        this.router.navigate(['/panel-taller']);
      },
      error: (err) => {

        // Si es administrador, no contar intentos
      if (this.esAdministrador()) {
        alert('❌ Credenciales inválidas. (Administrador sin límite de intentos)');
        return;
      }

        // Login fallido
        this.intentosFallidos++;
        
        if (this.intentosFallidos >= 3) {//// aqui son los intentos maximos antes de bloquear
          // Bloquear por 60 segundos
          this.bloqueado = true;
          this.tiempoRestante = 60;
          this.iniciarTemporizador();
          alert('❌ Demasiados intentos fallidos. Cuenta bloqueada por 1 minuto.');
          this.intentosFallidos = 0;
        } else {
          alert(`❌ Credenciales inválidas. Intentos restantes: ${3 - this.intentosFallidos}`); //aqui tambien cambiar  los intentos maximos
        }
      }
    });
  }

   // 🔥 INICIAR TEMPORIZADOR VISUAL
  iniciarTemporizador(): void {
    if (this.temporizador) clearInterval(this.temporizador);
    
    this.temporizador = setInterval(() => {
      if (this.tiempoRestante > 0) {
        this.tiempoRestante--;
      }
      
      if (this.tiempoRestante <= 0) {
        this.resetearBloqueo();
        clearInterval(this.temporizador);
        alert('✅ Bloqueo terminado. Ahora puedes intentar nuevamente.');
      }
    }, 1000);
  }

  // 🔥 RESETEAR BLOQUEO
  resetearBloqueo(): void {
    this.bloqueado = false;
    this.tiempoRestante = 0;
    this.intentosFallidos = 0;
    if (this.temporizador) {
      clearInterval(this.temporizador);
      this.temporizador = null;
    }
  }

  // 🔥 FUNCIÓN PARA DETECTAR SI ES ADMINISTRADOR
esAdministrador(): boolean {
  // Por email
  const email = this.loginData.email.toLowerCase();
  return email === 'dbanegas205@gmail.com' || 
         email === 'admin@emergauto.com' ||
         email.includes('admin');
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