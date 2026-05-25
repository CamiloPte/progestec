// src/app/client-portal/client-dashboard/client-dashboard.component.ts
import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { DashboardService } from '../../core/services/dashboard.service';
import { AuthService } from '../../core/services/auth.service';
import { ClientDashboardSummary, ClientTicketSummary, ClientDeviceSummary, ClientInvoiceSummary, ClientNotification } from '../../core/models/dashboard';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner.component';

@Component({
  selector: 'app-client-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink, LoadingSpinnerComponent],
  templateUrl: './client-dashboard.component.html',
  styleUrls: ['./client-dashboard.component.css'],
})
export class ClientDashboardComponent implements OnInit {
  summary: ClientDashboardSummary | null = null;
  loading = true;
  error: string | null = null;
  isBrowser: boolean;

  constructor(
    private dashboardService: DashboardService,
    private authService: AuthService,
    private router: Router,
    @Inject(PLATFORM_ID) platformId: object
  ) {
    this.isBrowser = isPlatformBrowser(platformId);
  }

  ngOnInit(): void {
    if (this.isBrowser) {
      this.loadDashboard();
    }
  }

  loadDashboard(): void {
    this.loading = true;
    this.error = null;
    
    this.dashboardService.getClientDashboard().subscribe({
      next: (data) => {
        this.summary = data;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error cargando dashboard:', err);
        this.error = 'No se pudo cargar el dashboard. Intenta de nuevo.';
        this.loading = false;
      }
    });
  }

  navigateToTicket(ticketId: number): void {
    this.router.navigate(['/client/tickets', ticketId]);
  }

  navigateToDevice(deviceId: number): void {
    this.router.navigate(['/client/devices', deviceId]);
  }

  navigateToInvoice(invoiceId: number): void {
    this.router.navigate(['/client/invoices', invoiceId]);
  }

  handleNotificationClick(notification: ClientNotification): void {
    if (notification.action_url) {
      this.router.navigateByUrl(notification.action_url);
    }
  }

  getDeviceIcon(type: string): string {
    const icons: Record<string, string> = {
      'PHONE': '📱',
      'LAPTOP': '💻',
      'TABLET': '📟',
      'OTHER': '🔧'
    };
    return icons[type.toUpperCase()] || '📦';
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

  getInvoiceStatusClass(status: string): string {
    const classes: Record<string, string> = {
      'PENDING': 'invoice-pending',
      'PARTIAL': 'invoice-partial',
      'PAID': 'invoice-paid',
      'CANCELLED': 'invoice-cancelled'
    };
    return classes[status.toUpperCase()] || '';
  }

  getInvoiceStatusLabel(status: string): string {
    const labels: Record<string, string> = {
      'PENDING': 'Pendiente',
      'PARTIAL': 'Pago parcial',
      'PAID': 'Pagada',
      'CANCELLED': 'Cancelada'
    };
    return labels[status.toUpperCase()] || status;
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
