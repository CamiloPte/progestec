// src/app/tickets/tickets-list/tickets-list.component.ts
import { Component, OnDestroy, OnInit, Inject } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { Subscription } from 'rxjs';

import {
  TicketService,
  TicketsListFilters,
  AssignedFilter,
} from '../../core/services/ticket.service';
import { AuthService } from '../../core/services/auth.service';
import { TicketReadMinimal } from '../../core/models/ticket';
import { CurrentUser } from '../../core/models/user';
import { AuthenticatedLayoutComponent } from '../../core/layouts/authenticated-layout.component';
import { PermissionService } from '../../core/services/permission.service';
import { PLATFORM_ID } from '@angular/core';

@Component({
  selector: 'app-tickets-list',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule, AuthenticatedLayoutComponent],
  templateUrl: './tickets-list.component.html',
  styleUrls: ['./tickets-list.component.css'],
})
export class TicketsListComponent implements OnInit, OnDestroy {
  tickets: TicketReadMinimal[] = [];

  loading = false;
  error: string | null = null;
  currentUser: CurrentUser | null = null;
  get isTechnician(): boolean {
    return this.permissionService.isTechnician(this.currentUser);
  }
  get canCreateTicket(): boolean {
    return this.permissionService.canCreateTicket(this.currentUser);
  }

  // Filtros
  statusFilterCode: string = 'ALL';
  assignedFilter: AssignedFilter = 'all';
  searchText: string = '';
  deviceTypeFilter: string = 'ALL';
  fromDate?: string;
  toDate?: string;

  // Opciones para selects
  statusOptions = [
    { code: 'ALL', label: 'Todos los estados' },
    { code: 'RECEIVED', label: 'Recibidos' },
    { code: 'DIAGNOSING', label: 'En diagnóstico' },
    { code: 'IN_PROGRESS', label: 'En progreso' },
    { code: 'READY', label: 'Listos para entrega' },
    { code: 'CLOSED', label: 'Cerrados' },
  ];

  assignedOptions: { code: AssignedFilter; label: string }[] = [];

  deviceTypeOptions = [
    { code: 'ALL', label: 'Todos los tipos' },
    { code: 'PHONE', label: 'Teléfonos' },
    { code: 'LAPTOP', label: 'Laptops' },
    { code: 'TABLET', label: 'Tablets' },
  ];

  private subs = new Subscription();
  private isBrowser = false;

  constructor(
    private ticketService: TicketService,
    private authService: AuthService,
    private permissionService: PermissionService,
    private router: Router,
    @Inject(PLATFORM_ID) private platformId: Object,
  ) {}

  ngOnInit(): void {
    this.isBrowser = isPlatformBrowser(this.platformId);
    if (!this.isBrowser) {
      return;
    }

    const userSub = this.authService.currentUser$.subscribe((user) => {
      this.currentUser = user;
      this.buildAssignedOptions();
    });
    this.subs.add(userSub);

    this.loadTickets();
  }

  ngOnDestroy(): void {
    this.subs.unsubscribe();
  }

  // Construye los filtros y llama al backend
  loadTickets(): void {
    if (!this.isBrowser) {
      return;
    }
    this.loading = true;
    this.error = null;

    const filters: TicketsListFilters = {};

    if (this.statusFilterCode && this.statusFilterCode !== 'ALL') {
      filters.status = [this.statusFilterCode];
    }

    if (this.assignedFilter) {
      filters.assigned = this.assignedFilter;
    }

    if (this.deviceTypeFilter && this.deviceTypeFilter !== 'ALL') {
      filters.device_type = this.deviceTypeFilter;
    }

    if (this.searchText && this.searchText.trim() !== '') {
      filters.search = this.searchText.trim();
    }

    if (this.fromDate) {
      filters.from_date = this.fromDate; // 'YYYY-MM-DD'
    }

    if (this.toDate) {
      filters.to_date = this.toDate;
    }

    this.ticketService.listTickets(filters).subscribe({
      next: (data) => {
        this.tickets = data;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error cargando tickets', err);
        this.error = 'No se pudieron cargar los tickets. Intenta de nuevo.';
        this.loading = false;
      },
    });
  }

  // Cualquier cambio en filtros vuelve a disparar la carga
  onFiltersChanged(): void {
    this.loadTickets();
  }

  clearFilters(): void {
    this.statusFilterCode = 'ALL';
    this.assignedFilter = 'all';
    this.searchText = '';
    this.deviceTypeFilter = 'ALL';
    this.fromDate = undefined;
    this.toDate = undefined;

    this.loadTickets();
  }

  goToDetail(id: number): void {
    // Cuando tengas el componente de detalle, asegúrate de tener la ruta:
    // { path: 'tickets/:id', loadComponent: () => import(...).then(m => m.TicketDetailComponent) }
    this.router.navigate(['/tickets', id]);
  }

  onCreateTicket(): void {
    this.router.navigate(['/tickets/new']);
  }

  // Clase de la "pill" de estado
  getStatusPillClass(ticket: TicketReadMinimal): string {
    const code = (ticket.status_code || '').toUpperCase();
    const name = (ticket.status_name || '').toLowerCase();

    // Recibido
    if (code === 'RECEIVED' || name.includes('recib')) {
      return 'status-pill--info';
    }
    // Diagnóstico
    if (code === 'DIAGNOSING' || name.includes('diag')) {
      return 'status-pill--diagnosis';
    }
    // Esperando aprobación
    if (code === 'WAITING_APPROVAL' || name.includes('aprobación') || name.includes('esperando')) {
      return 'status-pill--approval';
    }
    // En reparación / en progreso
    if (
      code === 'REPAIRING' ||
      code === 'PENDING' ||
      code === 'IN_PROGRESS' ||
      code === 'IN_REPAIR' ||
      name.includes('repar') ||
      name.includes('progreso')
    ) {
      return 'status-pill--warning';
    }
    // Listo / entregado / cerrado
    if (
      code === 'READY' ||
      code === 'DELIVERED' ||
      code === 'CLOSED' ||
      name.includes('listo') ||
      name.includes('entregado') ||
      name.includes('cerrado')
    ) {
      return 'status-pill--success';
    }
    // Cancelado
    if (code === 'CANCELLED' || name.includes('cancel')) {
      return 'status-pill--danger';
    }
    return 'status-pill--default';
  }

  private buildAssignedOptions(): void {
    const opts: { code: AssignedFilter; label: string }[] = [{
      code: 'all',
      label: 'Todos',
    }];
    if (this.isTechnician) {
      opts.push({ code: 'me', label: 'Asignados a mí' });
    }
    opts.push({ code: 'unassigned', label: 'Sin asignar' });
    this.assignedOptions = opts;

    if (!this.isTechnician && this.assignedFilter === 'me') {
      this.assignedFilter = 'all';
    }
  }
}
