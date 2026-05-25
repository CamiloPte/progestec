// src/app/client-portal/client-tickets/client-tickets.component.ts
import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { DashboardService } from '../../core/services/dashboard.service';
import { ClientDashboardSummary, ClientTicketSummary } from '../../core/models/dashboard';

@Component({
  selector: 'app-client-tickets',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './client-tickets.component.html',
  styleUrls: ['./client-tickets.component.css'],
})
export class ClientTicketsComponent implements OnInit {
  tickets: ClientTicketSummary[] = [];
  loading = true;
  error: string | null = null;
  isBrowser: boolean;
  
  filter: 'all' | 'active' | 'completed' = 'all';

  constructor(
    private dashboardService: DashboardService,
    private router: Router,
    @Inject(PLATFORM_ID) platformId: object
  ) {
    this.isBrowser = isPlatformBrowser(platformId);
  }

  ngOnInit(): void {
    if (this.isBrowser) {
      this.loadTickets();
    }
  }

  loadTickets(): void {
    this.loading = true;
    this.dashboardService.getClientDashboard().subscribe({
      next: (data) => {
        this.tickets = data.tickets;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error:', err);
        this.error = 'No se pudieron cargar los tickets.';
        this.loading = false;
      }
    });
  }

  get filteredTickets(): ClientTicketSummary[] {
    if (this.filter === 'all') return this.tickets;
    if (this.filter === 'active') {
      return this.tickets.filter(t => !['CLOSED', 'CANCELLED', 'DELIVERED'].includes(t.status_code.toUpperCase()));
    }
    return this.tickets.filter(t => ['CLOSED', 'CANCELLED', 'DELIVERED'].includes(t.status_code.toUpperCase()));
  }

  setFilter(filter: 'all' | 'active' | 'completed'): void {
    this.filter = filter;
  }

  navigateToTicket(ticketId: number): void {
    this.router.navigate(['/client/tickets', ticketId]);
  }

  goBack(): void {
    this.router.navigate(['/client/dashboard']);
  }

  getStatusBadgeClass(statusCode: string): string {
    const classes: Record<string, string> = {
      'RECEIVED': 'badge-info',
      'DIAGNOSING': 'badge-purple',
      'WAITING_APPROVAL': 'badge-warning',
      'APPROVED': 'badge-success',
      'IN_PROGRESS': 'badge-primary',
      'READY': 'badge-success',
      'DELIVERED': 'badge-teal',
      'CLOSED': 'badge-secondary',
      'CANCELLED': 'badge-danger'
    };
    return classes[statusCode.toUpperCase()] || 'badge-secondary';
  }
}
