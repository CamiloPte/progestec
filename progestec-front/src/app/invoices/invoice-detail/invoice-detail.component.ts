import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { Subscription } from 'rxjs';

import { AuthenticatedLayoutComponent } from '../../core/layouts/authenticated-layout.component';
import { InvoiceService } from '../../core/services/invoice.service';
import { Invoice, InvoicePaymentCreateDto, InvoiceUpdateDto } from '../../core/models/invoice';
import { PermissionService } from '../../core/services/permission.service';
import { AuthService } from '../../core/services/auth.service';
import { CurrentUser } from '../../core/models/user';

@Component({
  selector: 'app-invoice-detail',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule, AuthenticatedLayoutComponent],
  templateUrl: './invoice-detail.component.html',
  styleUrls: ['./invoice-detail.component.css'],
})
export class InvoiceDetailComponent implements OnInit, OnDestroy {
  invoice: Invoice | null = null;
  loading = false;
  error: string | null = null;
  currentUser: CurrentUser | null = null;
  downloadingPdf = false;
  private subs = new Subscription();

  // Formulario para editar factura DRAFT
  editForm: {
    labor_cost: number;
    discount_amount: number;
    tax_percentage: number;
    notes: string;
    saving: boolean;
    error: string;
  } = {
    labor_cost: 0,
    discount_amount: 0,
    tax_percentage: 19,
    notes: '',
    saving: false,
    error: '',
  };

  paymentForm: {
    amount: string;
    payment_method: string;
    reference: string;
    paid_at: string;
    saving: boolean;
    error: string;
  } = {
    amount: '',
    payment_method: 'CASH',
    reference: '',
    paid_at: '',
    saving: false,
    error: '',
  };

  constructor(
    private route: ActivatedRoute,
    private invoiceService: InvoiceService,
    private permissionService: PermissionService,
    private authService: AuthService,
  ) {}

  ngOnInit(): void {
    const sub = this.authService.currentUser$.subscribe((user) => {
      this.currentUser = user;
    });
    this.subs.add(sub);
    const idParam = this.route.snapshot.paramMap.get('id');
    const invoiceId = idParam ? Number(idParam) : NaN;
    if (!idParam || Number.isNaN(invoiceId)) {
      this.error = 'Factura inválida.';
      return;
    }
    this.loadInvoice(invoiceId);
  }

  ngOnDestroy(): void {
    this.subs.unsubscribe();
  }

  get canRegisterPayment(): boolean {
    return this.permissionService.canManageFinance(this.currentUser);
  }

  get canEditInvoice(): boolean {
    return (
      this.permissionService.canManageFinance(this.currentUser) &&
      this.invoice?.status?.toUpperCase() === 'DRAFT'
    );
  }

  get isDraft(): boolean {
    return this.invoice?.status?.toUpperCase() === 'DRAFT';
  }

  loadInvoice(id: number): void {
    this.loading = true;
    this.invoiceService.getInvoice(id).subscribe({
      next: (invoice) => {
        this.invoice = invoice;
        this.loading = false;
        // Inicializar formulario de edición con valores actuales
        if (invoice.status?.toUpperCase() === 'DRAFT') {
          this.editForm.labor_cost = invoice.labor_cost || 0;
          this.editForm.discount_amount = invoice.discount_amount || 0;
          this.editForm.tax_percentage = invoice.tax_percentage || 19;
          this.editForm.notes = invoice.notes || '';
        }
      },
      error: () => {
        this.error = 'No se pudo cargar la factura.';
        this.loading = false;
      },
    });
  }

  // Calcula la vista previa de totales para el formulario de edición
  get editPreview() {
    const parts = this.invoice?.parts_cost || 0;
    const labor = this.editForm.labor_cost || 0;
    const discount = this.editForm.discount_amount || 0;
    const taxPct = this.editForm.tax_percentage || 0;
    const subtotal = parts + labor - discount;
    const taxAmount = (subtotal * taxPct) / 100;
    const total = subtotal + taxAmount;
    return { parts, labor, discount, subtotal, taxPct, taxAmount, total };
  }

  // Guarda los cambios en la factura DRAFT (sin confirmar)
  saveInvoice(): void {
    if (!this.invoice || !this.canEditInvoice) return;
    
    this.editForm.saving = true;
    this.editForm.error = '';
    
    const payload: InvoiceUpdateDto = {
      labor_cost: this.editForm.labor_cost,
      discount_amount: this.editForm.discount_amount,
      tax_percentage: this.editForm.tax_percentage,
      notes: this.editForm.notes || undefined,
      confirm: false,
    };
    
    this.invoiceService.updateInvoice(this.invoice.id, payload).subscribe({
      next: (updated) => {
        this.invoice = updated;
        this.editForm.saving = false;
      },
      error: (err) => {
        this.editForm.error = err?.error?.detail || 'No se pudo guardar la factura.';
        this.editForm.saving = false;
      },
    });
  }

  // Confirma la factura (pasa de DRAFT a PENDING)
  confirmInvoice(): void {
    if (!this.invoice || !this.canEditInvoice) return;
    
    this.editForm.saving = true;
    this.editForm.error = '';
    
    const payload: InvoiceUpdateDto = {
      labor_cost: this.editForm.labor_cost,
      discount_amount: this.editForm.discount_amount,
      tax_percentage: this.editForm.tax_percentage,
      notes: this.editForm.notes || undefined,
      confirm: true,
    };
    
    this.invoiceService.updateInvoice(this.invoice.id, payload).subscribe({
      next: (updated) => {
        this.invoice = updated;
        this.editForm.saving = false;
      },
      error: (err) => {
        this.editForm.error = err?.error?.detail || 'No se pudo confirmar la factura.';
        this.editForm.saving = false;
      },
    });
  }

  getStatusBadgeClass(status: string): string {
    const normalized = (status || '').toUpperCase();
    if (normalized === 'PAID') {
      return 'status-chip--success';
    }
    if (normalized === 'PENDING') {
      return 'status-chip--warning';
    }
    return 'status-chip--neutral';
  }

  setFullPayment(): void {
    if (this.invoice) {
      this.paymentForm.amount = String(this.invoice.outstanding_amount);
    }
  }

  submitPayment(): void {
    if (!this.invoice) {
      return;
    }
    const amount = Number(this.paymentForm.amount);
    if (Number.isNaN(amount) || amount <= 0) {
      this.paymentForm.error = 'Ingresa un monto válido.';
      return;
    }
    const payload: InvoicePaymentCreateDto = {
      amount,
      payment_method: this.paymentForm.payment_method,
      reference: this.paymentForm.reference || undefined,
      paid_at: this.paymentForm.paid_at || undefined,
    };
    this.paymentForm.saving = true;
    this.paymentForm.error = '';
    this.invoiceService.registerPayment(this.invoice.id, payload).subscribe({
      next: (updated) => {
        this.invoice = updated;
        this.resetPaymentForm();
        this.paymentForm.saving = false;
      },
      error: () => {
        this.paymentForm.error = 'No se pudo registrar el pago.';
        this.paymentForm.saving = false;
      },
    });
  }

  private resetPaymentForm(): void {
    this.paymentForm = {
      amount: '',
      payment_method: 'CASH',
      reference: '',
      paid_at: '',
      saving: false,
      error: '',
    };
  }

  downloadPdf(): void {
    if (!this.invoice || this.downloadingPdf) return;
    
    this.downloadingPdf = true;
    this.invoiceService.downloadPdf(this.invoice.id).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `factura_${this.invoice?.invoice_number || this.invoice?.id}.pdf`;
        link.click();
        window.URL.revokeObjectURL(url);
        this.downloadingPdf = false;
      },
      error: () => {
        alert('No se pudo descargar el PDF.');
        this.downloadingPdf = false;
      },
    });
  }
}
