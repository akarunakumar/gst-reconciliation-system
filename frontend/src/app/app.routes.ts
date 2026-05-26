import { Routes } from '@angular/router';
import { authGuard } from './guards/auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
  {
    path: 'login',
    loadChildren: () => import('./modules/auth/auth.routes').then((m) => m.authRoutes),
  },
  {
    path: 'dashboard',
    canActivate: [authGuard],
    loadComponent: () => import('./modules/dashboard/dashboard.component').then((m) => m.DashboardComponent),
  },
  {
    path: 'reconciliation/:sessionId',
    canActivate: [authGuard],
    loadComponent: () => import('./modules/reconciliation/reconciliation.component').then((m) => m.ReconciliationComponent),
  },
  { path: '**', redirectTo: 'dashboard' },
];
