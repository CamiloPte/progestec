// src/app/client-portal/client-portal.routes.ts
import { Routes } from '@angular/router';
import { authGuard } from '../core/guards/auth.guard';

export const CLIENT_PORTAL_ROUTES: Routes = [
  {
    path: '',
    canActivate: [authGuard],
    children: [
      {
        path: '',
        redirectTo: 'dashboard',
        pathMatch: 'full'
      },
      {
        path: 'dashboard',
        loadComponent: () => import('./client-dashboard/client-dashboard.component')
          .then(m => m.ClientDashboardComponent),
        title: 'Mi Portal - ProGesTec'
      },
      {
        path: 'tickets',
        loadComponent: () => import('./client-tickets/client-tickets.component')
          .then(m => m.ClientTicketsComponent),
        title: 'Mis Tickets - ProGesTec'
      },
      {
        path: 'tickets/:id',
        loadComponent: () => import('./client-ticket-detail/client-ticket-detail.component')
          .then(m => m.ClientTicketDetailComponent),
        title: 'Detalle de Ticket - ProGesTec'
      },
      {
        path: 'devices',
        loadComponent: () => import('./client-devices/client-devices.component')
          .then(m => m.ClientDevicesComponent),
        title: 'Mis Dispositivos - ProGesTec'
      },
      {
        path: 'devices/:id',
        loadComponent: () => import('./client-device-detail/client-device-detail.component')
          .then(m => m.ClientDeviceDetailComponent),
        title: 'Detalle de Dispositivo - ProGesTec'
      },
      {
        path: 'invoices',
        loadComponent: () => import('./client-invoices/client-invoices.component')
          .then(m => m.ClientInvoicesComponent),
        title: 'Mis Facturas - ProGesTec'
      },
      {
        path: 'invoices/:id',
        loadComponent: () => import('./client-invoice-detail/client-invoice-detail.component')
          .then(m => m.ClientInvoiceDetailComponent),
        title: 'Detalle de Factura - ProGesTec'
      },
      {
        path: 'profile',
        loadComponent: () => import('./client-profile/client-profile.component')
          .then(m => m.ClientProfileComponent),
        title: 'Mi Perfil - ProGesTec'
      }
    ]
  }
];
