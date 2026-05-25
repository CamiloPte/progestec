import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { Subscription } from 'rxjs';

import { AuthenticatedLayoutComponent } from '../../core/layouts/authenticated-layout.component';
import { InvoiceService } from '../../core/services/invoice.service';
import { Invoice } from '../../core/models/invoice';
import { AuthService } from '../../core/services/auth.service';
import { CurrentUser } from '../../core/models/user';

@Component({
  selector: 'app-client-invoices',
  standalone: true,
  imports: [CommonModule, RouterModule, AuthenticatedLayoutComponent],
  templateUrl: './client-invoices.component.html',
  styleUrls: ['./client-invoices.component.css'],
})
export class ClientInvoicesComponent implements OnInit, OnDestroy {
  invoices: Invoice[] = [];
  loading = false;
  error: string | null = null;
  currentUser: CurrentUser | null = null;
  private subs = new Subscription();

  constructor(
    private invoiceService: InvoiceService,
    private authService: AuthService,
  ) {}

  ngOnInit(): void {
    const sub = this.authService.currentUser$.subscribe((user) => {
      this.currentUser = user;
      if (user) {
        this.loadInvoices(user.id);
      }
    });
    this.subs.add(sub);
  }

  ngOnDestroy(): void {
    this.subs.unsubscribe();
  }

  loadInvoices(clientId: number): void {
    this.loading = true;
    this.invoiceService.listInvoices({ client_id: clientId }).subscribe({
      next: (items) => {
        this.invoices = items;
        this.loading = false;
      },
      error: () => {
        this.error = 'No se pudieron cargar sus facturas.';
        this.loading = false;
      },
    });
  }

  getStatusBadgeClass(status: string): string {
    const normalized = (status || '').toUpperCase();
    if (normalized === 'PAID') {
      return 'status-badge success';
    }
    if (normalized === 'PENDING') {
      return 'status-badge warning';
    }
    return 'status-badge gray';
  }
}
