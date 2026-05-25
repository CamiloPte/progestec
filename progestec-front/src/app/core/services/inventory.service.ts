import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import { API_BASE_URL } from '../config/api.config';
import {
  InventorySummary,
  InventoryPart,
  InventoryPartDetail,
  InventoryPartMovement,
  InventoryFilters,
  MovementPayload,
  InventoryPartPayload,
} from '../models/inventory';

@Injectable({ providedIn: 'root' })
export class InventoryService {
  private baseUrl = `${API_BASE_URL}/inventory`;

  constructor(private http: HttpClient) {}

  getSummary(): Observable<InventorySummary> {
    return this.http.get<InventorySummary>(`${this.baseUrl}/summary`);
  }

  getParts(filters: InventoryFilters = {}): Observable<InventoryPart[]> {
    let params = new HttpParams();
    if (filters.search) {
      params = params.set('search', filters.search);
    }
    if (filters.category && filters.category !== 'ALL') {
      params = params.set('category', filters.category);
    }
    if (filters.status && filters.status !== 'ALL') {
      params = params.set('status', filters.status);
    }
    return this.http.get<InventoryPart[]>(`${this.baseUrl}/parts`, { params });
  }

  getPartDetail(id: number): Observable<InventoryPartDetail> {
    return this.http.get<InventoryPartDetail>(`${this.baseUrl}/parts/${id}`);
  }

  getMovements(id: number): Observable<InventoryPartMovement[]> {
    return this.http.get<InventoryPartMovement[]>(`${this.baseUrl}/parts/${id}/movements`);
  }

  registerMovement(id: number, payload: MovementPayload): Observable<InventoryPart> {
    return this.http.post<InventoryPart>(`${this.baseUrl}/parts/${id}/movements`, payload);
  }

  createPart(payload: InventoryPartPayload): Observable<InventoryPart> {
    return this.http.post<InventoryPart>(`${this.baseUrl}/parts`, payload);
  }

  updatePart(id: number, payload: Partial<InventoryPartPayload>): Observable<InventoryPart> {
    return this.http.put<InventoryPart>(`${this.baseUrl}/parts/${id}`, payload);
  }

  deletePart(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/parts/${id}`);
  }
}
