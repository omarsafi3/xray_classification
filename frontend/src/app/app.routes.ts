import { Routes } from '@angular/router';
import { GlobalMetricsList } from './global-metrics-list/global-metrics-list';
import { Login } from './login/login';
import { Signup } from './signup/signup';
import { AuthGuard } from './guards/auth.guard';
import { LoginGuard } from './guards/login.guard';
import { UploadImageComponent } from './upload-image/upload-image';
import { FlClientComponent } from './fl-client/fl-client';

export const routes: Routes = [
  { path: '', 
    redirectTo: 'home', 
    pathMatch: 'full' },

  {
    path: 'home',
    component: GlobalMetricsList,
  },
  {
    path: 'login',
    component: Login,
    canActivate: [LoginGuard] 
  },
  {
    path: 'signup',
    component: Signup,
    canActivate: [LoginGuard]
  },

  { path: 'upload',
    component: UploadImageComponent
  },

  {
    path: 'fl_client',
    component: FlClientComponent,
    canActivate: [AuthGuard]
  },

  { path: '**', 
    redirectTo: 'home' }
];
