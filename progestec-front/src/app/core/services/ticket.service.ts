// src/app/core/services/ticket.service.ts

import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import { API_BASE_URL } from '../config/api.config';
import {
  TicketReadMinimal,
  TicketReadDetail,
} from '../models/ticket';
import { TicketPartRead, TicketPartCreate } from '../models/ticket-part';

export type AssignedFilter = 'all' | 'me' | 'unassigned';

export interface TicketsListFilters {
  status?: string[];          // códigos: RECEIVED, READY, etc.
  assigned?: AssignedFilter;  // all | me | unassigned
  from_date?: string;         // ISO date-time o 'YYYY-MM-DD'
  to_date?: string;           // igual que from_date
  search?: string;
  device_type?: string;       // PHONE | LAPTOP | ...
}

@Injectable({
  providedIn: 'root',
})
export class TicketService {
  private baseUrl = `${API_BASE_URL}/tickets`;

  constructor(private http: HttpClient) {}

  // GET /tickets con filtros opcionales (mapeados al backend)
  listTickets(filters?: TicketsListFilters): Observable<TicketReadMinimal[]> {
    let params = new HttpParams();

    if (filters) {
      if (filters.status && filters.status.length > 0) {
        filters.status.forEach((code) => {
          params = params.append('status', code);
        });
      }

      if (filters.assigned) {
        params = params.set('assigned', filters.assigned);
      }

      if (filters.from_date) {
        params = params.set('from_date', filters.from_date);
      }

      if (filters.to_date) {
        params = params.set('to_date', filters.to_date);
      }

      if (filters.search && filters.search.trim() !== '') {
        params = params.set('search', filters.search.trim());
      }

      if (filters.device_type) {
        params = params.set('device_type', filters.device_type);
      }
    }

    return this.http.get<TicketReadMinimal[]>(this.baseUrl, { params });
  }

  // GET /tickets/{id} → detalle
  getTicketDetail(id: number): Observable<TicketReadDetail> {
    return this.http.get<TicketReadDetail>(`${this.baseUrl}/${id}`);
  }

  // POST /tickets
  // (Solo admin/asesor, el backend valida permisos)
  createTicket(payload: any): Observable<TicketReadDetail> {
    return this.http.post<TicketReadDetail>(this.baseUrl, payload);
  }

  // PUT /tickets/{id}
  updateTicket(id: number, payload: any): Observable<TicketReadDetail> {
    return this.http.put<TicketReadDetail>(`${this.baseUrl}/${id}`, payload);
  }

  // PATCH /tickets/{id}/assign
  assignTicket(ticketId: number, technicianId: number | null): Observable<TicketReadDetail> {
    return this.http.patch<TicketReadDetail>(`${this.baseUrl}/${ticketId}/assign`, {
      assignee_user_id: technicianId,
    });
  }

  // POST /tickets/{id}/attachments
  uploadAttachment(ticketId: number, formData: FormData): Observable<any> {
    return this.http.post(`${this.baseUrl}/${ticketId}/attachments`, formData);
  }

  deleteAttachment(ticketId: number, attachmentId: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${ticketId}/attachments/${attachmentId}`);
  }

  listTicketParts(ticketId: number): Observable<TicketPartRead[]> {
    return this.http.get<TicketPartRead[]>(`${this.baseUrl}/${ticketId}/parts`);
  }

  addTicketPart(ticketId: number, payload: TicketPartCreate): Observable<TicketPartRead> {
    return this.http.post<TicketPartRead>(`${this.baseUrl}/${ticketId}/parts`, payload);
  }

  removeTicketPart(ticketId: number, ticketPartId: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${ticketId}/parts/${ticketPartId}`);
  }

  /**
   * Descarga el PDF del comprobante de recepción
   */
  downloadReceptionPdf(ticketId: number): Observable<Blob> {
    return this.http.get(`${this.baseUrl}/${ticketId}/pdf/reception`, {
      responseType: 'blob',
    });
  }

  /**
   * Descarga el PDF de la orden de entrega
   */
  downloadDeliveryPdf(ticketId: number): Observable<Blob> {
    return this.http.get(`${this.baseUrl}/${ticketId}/pdf/delivery`, {
      responseType: 'blob',
    });
  }

  /**
   * Responde a una cotización (aprobar o rechazar)
   * Solo disponible cuando el ticket está en WAITING_APPROVAL
   */
  respondToQuote(ticketId: number, approved: boolean, rejectionReason?: string): Observable<TicketReadDetail> {
    return this.http.patch<TicketReadDetail>(`${this.baseUrl}/${ticketId}/quote-response`, {
      approved,
      rejection_reason: rejectionReason || null,
    });
  }
}
