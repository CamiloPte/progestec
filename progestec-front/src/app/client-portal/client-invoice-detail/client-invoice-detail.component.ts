// src/app/client-portal/client-invoice-detail/client-invoice-detail.component.ts
import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { InvoiceService } from '../../core/services/invoice.service';

@Component({
  selector: 'app-client-invoice-detail',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="client-page">
      <header class="page-header">
        <button class="btn-back" (click)="goBack()">← Volver</button>
        <h1>Detalle de Factura</h1>
      </header>

      @if (loading) {
        <div class="loading-container">
          <div class="spinner"></div>
          <p>Cargando factura...</p>
        </div>
      } @else if (invoice) {
        <div class="invoice-detail-card">
          <div class="invoice-header">
            <div>
              <span class="label">Factura</span>
              <h2>{{ invoice.invoice_number }}</h2>
            </div>
            <span class="status-badge" [class]="'status-' + invoice.status.toLowerCase()">
              {{ getStatusLabel(invoice.status) }}
            </span>
          </div>

          <div class="invoice-info-grid">
            <div class="info-item">
              <span class="label">Fecha de emisión</span>
              <span class="value">{{ invoice.issue_date | date:'dd/MM/yyyy' }}</span>
            </div>
            @if (invoice.due_date) {
              <div class="info-item">
                <span class="label">Fecha de vencimiento</span>
                <span class="value">{{ invoice.due_date | date:'dd/MM/yyyy' }}</span>
              </div>
            }
            @if (invoice.ticket_tracking_code) {
              <div class="info-item">
                <span class="label">Ticket</span>
                <span class="value">{{ invoice.ticket_tracking_code }}</span>
              </div>
            }
          </div>

          <div class="invoice-amounts">
            <div class="amount-row">
              <span>Costo de repuestos</span>
              <span>\${{ invoice.parts_cost | number:'1.0-0' }}</span>
            </div>
            <div class="amount-row">
              <span>Mano de obra</span>
              <span>\${{ invoice.labor_cost | number:'1.0-0' }}</span>
            </div>
            @if (invoice.discount_amount > 0) {
              <div class="amount-row discount">
                <span>Descuento</span>
                <span>-\${{ invoice.discount_amount | number:'1.0-0' }}</span>
              </div>
            }
            <div class="amount-row subtotal">
              <span>Subtotal</span>
              <span>\${{ invoice.subtotal | number:'1.0-0' }}</span>
            </div>
            @if (invoice.tax_amount > 0) {
              <div class="amount-row">
                <span>IVA ({{ invoice.tax_percentage }}%)</span>
                <span>\${{ invoice.tax_amount | number:'1.0-0' }}</span>
              </div>
            }
            <div class="amount-row total">
              <span>TOTAL</span>
              <span>\${{ invoice.total | number:'1.0-0' }}</span>
            </div>
            @if (invoice.paid_amount > 0) {
              <div class="amount-row paid">
                <span>Pagado</span>
                <span>\${{ invoice.paid_amount | number:'1.0-0' }}</span>
              </div>
            }
            @if (invoice.pending_amount > 0) {
              <div class="amount-row pending">
                <span>Pendiente</span>
                <span class="pending-value">\${{ invoice.pending_amount | number:'1.0-0' }}</span>
              </div>
            }
          </div>

          <div class="invoice-actions">
            <button class="btn-download" (click)="downloadPdf()" [disabled]="downloadingPdf">
              @if (downloadingPdf) { Descargando... } @else { 📄 Descargar PDF }
            </button>
          </div>
        </div>
      }
    </div>
  `,
  styles: [`
    .client-page { min-height: 100vh; background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%); padding: 1.5rem; max-width: 600px; margin: 0 auto; }
    .page-header { display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem; }
    .btn-back { background: white; border: 1px solid #ddd; padding: 0.5rem 1rem; border-radius: 8px; cursor: pointer; }
    .page-header h1 { margin: 0; color: #1a5c3a; font-size: 1.5rem; }
    .loading-container { display: flex; flex-direction: column; align-items: center; padding: 3rem; }
    .spinner { width: 40px; height: 40px; border: 3px solid #e0e0e0; border-top-color: #1a5c3a; border-radius: 50%; animation: spin 1s linear infinite; }
    @keyframes spin { to { transform: rotate(360deg); } }
    .invoice-detail-card { background: white; border-radius: 16px; padding: 1.5rem; box-shadow: 0 2px 10px rgba(0,0,0,0.06); }
    .invoice-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem; }
    .invoice-header .label { font-size: 0.8rem; color: #999; }
    .invoice-header h2 { margin: 0.25rem 0 0; color: #1a5c3a; }
    .status-badge { padding: 0.5rem 1rem; border-radius: 20px; font-weight: 500; }
    .status-pending { background: #ffebee; color: #d32f2f; }
    .status-partial { background: #fff3e0; color: #f57c00; }
    .status-paid { background: #e8f5e9; color: #388e3c; }
    .invoice-info-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-bottom: 1.5rem; padding-bottom: 1.5rem; border-bottom: 1px solid #eee; }
    .info-item .label { display: block; font-size: 0.8rem; color: #999; }
    .info-item .value { color: #333; font-weight: 500; }
    .invoice-amounts { margin-bottom: 1.5rem; }
    .amount-row { display: flex; justify-content: space-between; padding: 0.5rem 0; }
    .amount-row.subtotal { border-top: 1px dashed #ddd; margin-top: 0.5rem; padding-top: 1rem; }
    .amount-row.total { font-size: 1.25rem; font-weight: 700; color: #1a5c3a; border-top: 2px solid #1a5c3a; margin-top: 0.5rem; padding-top: 1rem; }
    .amount-row.discount { color: #27ae60; }
    .amount-row.paid { color: #27ae60; }
    .amount-row.pending { color: #e74c3c; font-weight: 600; }
    .pending-value { font-size: 1.1rem; }
    .invoice-actions { text-align: center; }
    .btn-download { background: #1a5c3a; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 8px; cursor: pointer; font-size: 1rem; }
    .btn-download:hover:not(:disabled) { background: #155230; }
    .btn-download:disabled { opacity: 0.7; cursor: not-allowed; }
  `]
})
export class ClientInvoiceDetailComponent implements OnInit {
  invoice: any = null;
  loading = true;
  downloadingPdf = false;
  isBrowser: boolean;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private invoiceService: InvoiceService,
    @Inject(PLATFORM_ID) platformId: object
  ) {
    this.isBrowser = isPlatformBrowser(platformId);
  }

  ngOnInit(): void {
    if (this.isBrowser) {
      const id = Number(this.route.snapshot.paramMap.get('id'));
      if (id) this.loadInvoice(id);
    }
  }

  loadInvoice(id: number): void {
    this.invoiceService.getInvoice(id).subscribe({
      next: (data: any) => {
        this.invoice = data;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    });
  }

  goBack(): void {
    this.router.navigate(['/client/invoices']);
  }

  getStatusLabel(status: string): string {
    const labels: Record<string, string> = {
      'PENDING': 'Pendiente', 'PARTIAL': 'Pago parcial', 'PAID': 'Pagada', 'CANCELLED': 'Cancelada'
    };
    return labels[status?.toUpperCase()] || status;
  }

  downloadPdf(): void {
    if (!this.invoice) return;
    this.downloadingPdf = true;
    this.invoiceService.downloadPdf(this.invoice.id).subscribe({
      next: (blob: Blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `factura_${this.invoice.invoice_number}.pdf`;
        a.click();
        window.URL.revokeObjectURL(url);
        this.downloadingPdf = false;
      },
      error: () => {
        alert('No se pudo descargar el PDF.');
        this.downloadingPdf = false;
      }
    });
  }
}
