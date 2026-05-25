import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { API_BASE_URL } from '../config/api.config';
import { TicketStatusRead } from '../models/ticket-status';

@Injectable({
  providedIn: 'root',
})
export class TicketStatusService {
  private readonly baseUrl = `${API_BASE_URL}/ticket-statuses`;

  constructor(private http: HttpClient) {}

  listStatuses(): Observable<TicketStatusRead[]> {
    return this.http.get<TicketStatusRead[]>(this.baseUrl);
  }

  /**
   * Obtiene los estados válidos a los que se puede transicionar desde el estado actual.
   * El backend filtra según el rol del usuario autenticado.
   */
  getValidTransitions(currentStatusCode: string): Observable<TicketStatusRead[]> {
    return this.http.get<TicketStatusRead[]>(`${this.baseUrl}/transitions/${currentStatusCode}`);
  }
}
