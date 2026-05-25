// src/app/client-portal/client-invoices/client-invoices.component.ts
import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { InvoiceService } from '../../core/services/invoice.service';

@Component({
  selector: 'app-client-invoices',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <div class="client-page">
      <header class="page-header">
        <button class="btn-back" (click)="goBack()">← Volver</button>
        <h1>📄 Mis Facturas</h1>
      </header>

      @if (loading) {
        <div class="loading-container">
          <div class="spinner"></div>
          <p>Cargando facturas...</p>
        </div>
      } @else if (invoices.length === 0) {
        <div class="empty-state">
          <span class="empty-icon">📄</span>
          <h3>Sin facturas</h3>
          <p>No tienes facturas registradas.</p>
        </div>
      } @else {
        <div class="invoices-list">
          @for (inv of invoices; track inv.id) {
            <div class="invoice-card" [class]="getStatusClass(inv.status)" (click)="navigateToInvoice(inv.id)">
              <div class="invoice-header">
                <span class="invoice-number">{{ inv.invoice_number }}</span>
                <span class="invoice-status-badge" [class]="'status-' + inv.status.toLowerCase()">
                  {{ getStatusLabel(inv.status) }}
                </span>
              </div>
              <div class="invoice-info">
                <span class="invoice-date">{{ inv.issue_date | date:'dd/MM/yyyy' }}</span>
                @if (inv.ticket_tracking_code) {
                  <span class="invoice-ticket">Ticket: {{ inv.ticket_tracking_code }}</span>
                }
              </div>
              <div class="invoice-amount">
                <span class="amount-label">Total:</span>
                <span class="amount-value">\${{ inv.total | number:'1.0-0' }}</span>
              </div>
            </div>
          }
        </div>
      }
    </div>
  `,
  styles: [`
    .client-page { min-height: 100vh; background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%); padding: 1.5rem; }
    .page-header { display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem; }
    .btn-back { background: white; border: 1px solid #ddd; padding: 0.5rem 1rem; border-radius: 8px; cursor: pointer; }
    .page-header h1 { margin: 0; color: #1a5c3a; font-size: 1.5rem; }
    .loading-container { display: flex; flex-direction: column; align-items: center; padding: 3rem; }
    .spinner { width: 40px; height: 40px; border: 3px solid #e0e0e0; border-top-color: #1a5c3a; border-radius: 50%; animation: spin 1s linear infinite; }
    @keyframes spin { to { transform: rotate(360deg); } }
    .empty-state { text-align: center; padding: 3rem; background: white; border-radius: 12px; }
    .empty-icon { font-size: 3rem; }
    .invoices-list { display: flex; flex-direction: column; gap: 1rem; }
    .invoice-card { background: white; border-radius: 12px; padding: 1.25rem; cursor: pointer; box-shadow: 0 2px 8px rgba(0,0,0,0.06); transition: all 0.2s; border-left: 4px solid #ccc; }
    .invoice-card:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
    .invoice-card.pending { border-left-color: #e74c3c; }
    .invoice-card.partial { border-left-color: #f39c12; }
    .invoice-card.paid { border-left-color: #27ae60; }
    .invoice-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }
    .invoice-number { font-weight: 600; color: #333; font-size: 1.1rem; }
    .invoice-status-badge { padding: 0.25rem 0.75rem; border-radius: 15px; font-size: 0.8rem; font-weight: 500; }
    .status-pending { background: #ffebee; color: #d32f2f; }
    .status-partial { background: #fff3e0; color: #f57c00; }
    .status-paid { background: #e8f5e9; color: #388e3c; }
    .status-cancelled { background: #f5f5f5; color: #757575; }
    .invoice-info { display: flex; gap: 1rem; color: #666; font-size: 0.9rem; margin-bottom: 0.75rem; }
    .invoice-amount { display: flex; justify-content: space-between; align-items: center; padding-top: 0.75rem; border-top: 1px solid #eee; }
    .amount-label { color: #666; }
    .amount-value { font-size: 1.25rem; font-weight: 700; color: #1a5c3a; }
  `]
})
export class ClientInvoicesComponent implements OnInit {
  invoices: any[] = [];
  loading = true;
  isBrowser: boolean;

  constructor(
    private invoiceService: InvoiceService,
    private router: Router,
    @Inject(PLATFORM_ID) platformId: object
  ) {
    this.isBrowser = isPlatformBrowser(platformId);
  }

  ngOnInit(): void {
    if (this.isBrowser) {
      this.loadInvoices();
    }
  }

  loadInvoices(): void {
    this.invoiceService.listInvoices().subscribe({
      next: (data: any[]) => {
        this.invoices = data;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    });
  }

  goBack(): void {
    this.router.navigate(['/client/dashboard']);
  }

  navigateToInvoice(id: number): void {
    this.router.navigate(['/client/invoices', id]);
  }

  getStatusClass(status: string): string {
    return status.toLowerCase();
  }

  getStatusLabel(status: string): string {
    const labels: Record<string, string> = {
      'PENDING': 'Pendiente', 'PARTIAL': 'Pago parcial', 'PAID': 'Pagada', 'CANCELLED': 'Cancelada'
    };
    return labels[status.toUpperCase()] || status;
  }
}
