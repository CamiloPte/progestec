import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, map } from 'rxjs';

import { API_BASE_URL } from '../config/api.config';
import {
  Invoice,
  InvoiceCreateDto,
  InvoiceUpdateDto,
  InvoicePayment,
  InvoicePaymentCreateDto,
  InvoiceFilters,
} from '../models/invoice';

@Injectable({ providedIn: 'root' })
export class InvoiceService {
  private baseUrl = `${API_BASE_URL}/invoices`;

  constructor(private http: HttpClient) {}

  createInvoiceFromTicket(ticketId: number, payload: InvoiceCreateDto): Observable<Invoice> {
    return this.http.post<Invoice>(`${this.baseUrl}/from-ticket/${ticketId}`, payload);
  }

  getInvoice(invoiceId: number): Observable<Invoice> {
    return this.http.get<Invoice>(`${this.baseUrl}/${invoiceId}`);
  }

  updateInvoice(invoiceId: number, payload: InvoiceUpdateDto): Observable<Invoice> {
    return this.http.patch<Invoice>(`${this.baseUrl}/${invoiceId}`, payload);
  }

  listInvoices(filters?: InvoiceFilters): Observable<Invoice[]> {
    let params = new HttpParams();
    if (filters) {
      if (filters.status?.length) {
        filters.status.forEach((s) => {
          params = params.append('status', s);
        });
      }
      if (filters.client_id) {
        params = params.set('client_id', filters.client_id);
      }
      if (filters.from_date) {
        params = params.set('from_date', filters.from_date);
      }
      if (filters.to_date) {
        params = params.set('to_date', filters.to_date);
      }
      if (filters.with_debt !== undefined) {
        params = params.set('with_debt', String(filters.with_debt));
      }
      if (filters.ticket_id) {
        params = params.set('ticket_id', String(filters.ticket_id));
      }
    }
    return this.http.get<Invoice[]>(this.baseUrl, { params });
  }

  getInvoiceForTicket(ticketId: number): Observable<Invoice | null> {
    return this.listInvoices({ ticket_id: ticketId }).pipe(
      map((rows) => rows.find((inv) => inv.ticket_id === ticketId) ?? null)
    );
  }

  registerPayment(invoiceId: number, payload: InvoicePaymentCreateDto): Observable<Invoice> {
    return this.http.post<Invoice>(`${this.baseUrl}/${invoiceId}/payments`, payload);
  }

  listPayments(invoiceId: number): Observable<InvoicePayment[]> {
    return this.http.get<InvoicePayment[]>(`${this.baseUrl}/${invoiceId}/payments`);
  }

  /**
   * Descarga el PDF de la factura
   */
  downloadPdf(invoiceId: number): Observable<Blob> {
    return this.http.get(`${this.baseUrl}/${invoiceId}/pdf`, {
      responseType: 'blob',
    });
  }
}
