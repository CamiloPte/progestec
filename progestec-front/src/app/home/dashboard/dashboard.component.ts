// src/app/home/dashboard/dashboard.component.ts
import { Component, OnInit, Inject } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, filter, take } from 'rxjs';

import { AuthService } from '../../core/services/auth.service';
import { DashboardService } from '../../core/services/dashboard.service';
import { AuthenticatedLayoutComponent } from '../../core/layouts/authenticated-layout.component';

import { DashboardSummary, DashboardStatusCount } from '../../core/models/dashboard';
import { TicketReadMinimal } from '../../core/models/ticket';
import { CurrentUser } from '../../core/models/user';
import { PermissionService } from '../../core/services/permission.service';
import { PLATFORM_ID } from '@angular/core';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, AuthenticatedLayoutComponent],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css'],
})
export class DashboardComponent implements OnInit {
  // Usuario actual (para el saludo y lógica por rol)
  user$: Observable<CurrentUser | null>;

  // Resumen del dashboard
  summary: DashboardSummary | null = null;
  summaryLoading = false;
  summaryError: string | null = null;
  currentUser: CurrentUser | null = null;
  private isBrowser = false;

  constructor(
    private authService: AuthService,
    private dashboardService: DashboardService,
    private router: Router,
    private permissionService: PermissionService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {
    this.user$ = this.authService.currentUser$;
  }

  ngOnInit(): void {
    this.isBrowser = isPlatformBrowser(this.platformId);
    if (!this.isBrowser) {
      return;
    }

    this.authService.currentUser$
      .pipe(
        filter((user): user is CurrentUser => !!user),
        take(1)
      )
      .subscribe((user) => {
        this.currentUser = user;
        this.loadSummary();
      });
  }

  private loadSummary(): void {
    if (!this.isBrowser) {
      return;
    }
    this.summaryLoading = true;
    this.summaryError = null;

    this.dashboardService.getSummary().subscribe({
      next: (data) => {
        this.summary = data;
        this.summaryLoading = false;
      },
      error: (err) => {
        console.error('Error al cargar el resumen del dashboard', err);
        if (err instanceof HttpErrorResponse && err.status === 401) {
          this.authService.logout();
          this.router.navigate(['/login']);
          return;
        }
        this.summaryError = 'No se pudo cargar el resumen de tickets.';
        this.summaryLoading = false;
      },
    });
  }

  // Navegar a crear ticket
  onCreateTicket(): void {
    this.router.navigate(['/tickets/new']);
  }

  get canCreateTicket(): boolean {
    return this.permissionService.canCreateTicket(this.currentUser);
  }

  // Navegar al detalle de un ticket (por ahora asumimos que tendrás /tickets/:id)
  onViewTicket(ticket: TicketReadMinimal): void {
    this.router.navigate(['/tickets', ticket.id]);
  }

  // Porcentaje para la barra de "Tickets por estado"
  getStatusProgress(status: DashboardStatusCount): number {
    if (!this.summary || !this.summary.total_tickets) {
      return 0;
    }
    const total = this.summary.total_tickets;
    const ratio = (status.count / total) * 100;
    return Math.round(ratio);
  }

  // Clase visual para la barra según el status_code
  getStatusProgressClass(status: DashboardStatusCount): string {
    const code = (status.status_code || '').toUpperCase();

    switch (code) {
      case 'RECEIVED':
      case 'OPEN':
        return 'bg-primary';
      case 'DIAGNOSING':
        return 'bg-info';
      case 'WAITING_APPROVAL':
        return 'bg-approval';
      case 'REPAIRING':
      case 'IN_PROGRESS':
      case 'IN_REPAIR':
        return 'bg-warning';
      case 'READY':
      case 'DELIVERED':
      case 'CLOSED':
        return 'bg-success';
      default:
        return 'bg-light';
    }
  }

  // Badge de estado para la tabla de Recent Tickets
  getStatusBadgeClass(ticket: TicketReadMinimal): string {
    const code = (ticket.status_code || '').toUpperCase();

    switch (code) {
      case 'RECEIVED':
      case 'OPEN':
        return 'bg-primary-subtle text-primary border border-primary-subtle';
      case 'DIAGNOSING':
        return 'bg-info-subtle text-info border border-info-subtle';
      case 'WAITING_APPROVAL':
        return 'bg-approval-subtle text-approval border border-approval-subtle';
      case 'REPAIRING':
      case 'IN_PROGRESS':
      case 'IN_REPAIR':
        return 'bg-warning-subtle text-warning border border-warning-subtle';
      case 'READY':
      case 'DELIVERED':
      case 'CLOSED':
        return 'bg-success-subtle text-success border border-success-subtle';
      default:
        return 'bg-light text-muted border border-light';
    }
  }

}
