// src/app/app.routes.ts
import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { redirectIfAuthenticatedGuard } from './core/guards/redirect-if-authenticated.guard';
import { createTicketGuard } from './core/guards/create-ticket.guard';
import { inventoryGuard } from './core/guards/inventory.guard';
import { financeGuard } from './core/guards/finance.guard';
import { clientGuard } from './core/guards/client.guard';
import { usersGuard } from './core/guards/users.guard';
import { mustChangePasswordGuard, requirePasswordChangeGuard } from './core/guards/password-change.guard';

export const routes: Routes = [
  {
    path: 'login',
    loadComponent: () =>
      import('./auth/login/login.component').then(
        (m) => m.LoginComponent
      ),
    canActivate: [redirectIfAuthenticatedGuard],
  },
  {
    path: 'change-password',
    loadComponent: () =>
      import('./auth/change-password/change-password.component').then(
        (m) => m.ChangePasswordComponent
      ),
    canActivate: [authGuard, requirePasswordChangeGuard],
  },
  {
    path: 'inicio',
    canActivate: [authGuard, mustChangePasswordGuard],
    loadComponent: () =>
      import('./home/dashboard/dashboard.component').then(
        (m) => m.DashboardComponent
      ),
  },
  // Portal del Cliente - rutas dedicadas
  {
    path: 'client',
    canActivate: [authGuard, mustChangePasswordGuard, clientGuard],
    loadChildren: () =>
      import('./client-portal/client-portal.routes').then(
        (m) => m.CLIENT_PORTAL_ROUTES
      ),
  },
  // Gestión de usuarios - solo ADMIN
  {
    path: 'usuarios',
    canActivate: [authGuard, mustChangePasswordGuard, usersGuard],
    children: [
      {
        path: '',
        loadComponent: () =>
          import('./users/users-list/users-list.component').then(
            (m) => m.UsersListComponent
          ),
      },
    ],
  },
  {
    path: 'tickets',
    canActivate: [authGuard, mustChangePasswordGuard],
    children: [
      {
        path: '',
        loadComponent: () =>
          import('./tickets/tickets-list/tickets-list.component').then(
            (m) => m.TicketsListComponent
          ),
      },
      {
        path: 'new',
        loadComponent: () =>
          import('./tickets/ticket-create/ticket-create.component').then(
            (m) => m.TicketCreateComponent
          ),
        canActivate: [createTicketGuard],
      },
      {
        path: ':id',
        loadComponent: () =>
          import('./tickets/ticket-detail/ticket-detail.component').then(
            (m) => m.TicketDetailComponent
          ),
      },
    ],
  },
  {
    path: 'inventario',
    canActivate: [authGuard, mustChangePasswordGuard, inventoryGuard],
    children: [
      {
        path: '',
        loadComponent: () =>
          import('./inventory/inventory-dashboard/inventory-dashboard.component').then(
            (m) => m.InventoryDashboardComponent
          ),
      },
      {
        path: ':id',
        loadComponent: () =>
          import('./inventory/inventory-detail/inventory-detail.component').then(
            (m) => m.InventoryDetailComponent
          ),
      },
    ],
  },
  {
    path: 'facturacion',
    canActivate: [authGuard, mustChangePasswordGuard, financeGuard],
    children: [
      {
        path: '',
        loadComponent: () =>
          import('./invoices/invoice-list/invoice-list.component').then(
            (m) => m.InvoiceListComponent
          ),
      },
      {
        path: ':id',
        loadComponent: () =>
          import('./invoices/invoice-detail/invoice-detail.component').then(
            (m) => m.InvoiceDetailComponent
          ),
      },
    ],
  },
  {
    path: 'finanzas',
    canActivate: [authGuard, mustChangePasswordGuard, financeGuard],
    children: [
      {
        path: '',
        loadComponent: () =>
          import('./finances/finance-dashboard/finance-dashboard.component').then(
            (m) => m.FinanceDashboardComponent
          ),
      },
      {
        path: 'facturas',
        loadComponent: () =>
          import('./invoices/invoice-list/invoice-list.component').then(
            (m) => m.InvoiceListComponent
          ),
      },
      {
        path: 'facturas/:id',
        loadComponent: () =>
          import('./invoices/invoice-detail/invoice-detail.component').then(
            (m) => m.InvoiceDetailComponent
          ),
      },
      {
        path: 'gastos',
        loadComponent: () =>
          import('./finances/expense-list/expense-list.component').then(
            (m) => m.ExpenseListComponent
          ),
      },
    ],
  },
  {
    path: 'mis-facturas',
    canActivate: [authGuard, mustChangePasswordGuard, clientGuard],
    children: [
      {
        path: '',
        loadComponent: () =>
          import('./invoices/client-invoices/client-invoices.component').then(
            (m) => m.ClientInvoicesComponent
          ),
      },
      {
        path: ':id',
        loadComponent: () =>
          import('./invoices/invoice-detail/invoice-detail.component').then(
            (m) => m.InvoiceDetailComponent
          ),
      },
    ],
  },
  {
    path: '',
    pathMatch: 'full',
    redirectTo: 'login',
  },
  {
    path: '**',
    redirectTo: 'login',
  },
];
