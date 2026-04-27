import { Routes } from '@angular/router';
import { HomeComponent } from './Pagina/Home-Inicio/home.component';
import { AuthComponent } from './Pagina/Authenticacion-acesso/auth.component';/*para acesso cliente*/ 
import { AdminLoginComponent } from './Pagina/Admin-Login/admin-login.component';/*para aceeso cliente */
import { PanelAdminComponent } from './Pagina/Panel-Admin/panel-admin.component';/*Panel o interfaz del administrador */
import { PanelTallerComponent } from './Pagina/Panel-Taller/panel-taller.component';/*Panel o interfaz del taller */
import { ResetPasswordComponent } from './Pagina/ResetPassword/reset-password.component';/*Componente para resetear contraseña */

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'login', component: AuthComponent },
  { path: 'admin-login', component: AdminLoginComponent },
  { path: 'panel-taller', component: PanelTallerComponent },
  { path: 'panel-admin', component: PanelAdminComponent },
  { path: 'reset-password', component: ResetPasswordComponent }  // NUEVA RUTA
];