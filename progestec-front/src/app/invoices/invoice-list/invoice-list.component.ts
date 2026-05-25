import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { Subscription } from 'rxjs';

import { AuthenticatedLayoutComponent } from '../../core/layouts/authenticated-layout.component';
import { InvoiceService } from '../../core/services/invoice.service';
import { Invoice, InvoiceFilters } from '../../core/models/invoice';
import { AuthService } from '../../core/services/auth.service';
import { CurrentUser } from '../../core/models/user';

@Component({
  selector: 'app-invoice-list',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule, AuthenticatedLayoutComponent],
  templateUrl: './invoice-list.component.html',
  styleUrls: ['./invoice-list.component.css'],
})
export class InvoiceListComponent implements OnInit, OnDestroy {
  invoices: Invoice[] = [];
  loading = false;
  error: string | null = null;

  filters: {
    status: string;
    client: string;
    from_date: string;
    to_date: string;
    with_debt: boolean;
  } = {
    status: '',
    client: '',
    from_date: '',
    to_date: '',
    with_debt: false,
  };

  private subs = new Subscription();
  currentUser: CurrentUser | null = null;

  constructor(
    private invoiceService: InvoiceService,
    private authService: AuthService,
  ) {}

  ngOnInit(): void {
    const sub = this.authService.currentUser$.subscribe((user) => {
      this.currentUser = user;
    });
    this.subs.add(sub);
    this.loadInvoices();
  }

  ngOnDestroy(): void {
    this.subs.unsubscribe();
  }

  loadInvoices(): void {
    this.loading = true;
    this.error = null;

    const params: InvoiceFilters = {};
    if (this.filters.status) {
      params.status = [this.filters.status];
    }
    if (this.filters.client.trim()) {
      const clientId = Number(this.filters.client);
      if (!Number.isNaN(clientId)) {
        params.client_id = clientId;
      }
    }
    if (this.filters.from_date) {
      params.from_date = this.filters.from_date;
    }
    if (this.filters.to_date) {
      params.to_date = this.filters.to_date;
    }
    if (this.filters.with_debt) {
      params.with_debt = true;
    }

    this.invoiceService.listInvoices(params).subscribe({
      next: (items) => {
        this.invoices = items;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error cargando facturas', err);
        if (err?.status === 404) {
          this.invoices = [];
          this.error = null;
        } else {
          this.error = 'No se pudieron cargar las facturas.';
        }
        this.loading = false;
      },
    });
  }

  clearFilters(): void {
    this.filters = {
      status: '',
      client: '',
      from_date: '',
      to_date: '',
      with_debt: false,
    };
    this.loadInvoices();
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
}
