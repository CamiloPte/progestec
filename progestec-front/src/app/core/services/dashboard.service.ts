import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { DashboardSummary, ClientDashboardSummary } from '../models/dashboard';
import { API_BASE_URL } from '../config/api.config';

@Injectable({
  providedIn: 'root',
})
export class DashboardService {
  private readonly baseUrl = `${API_BASE_URL}/dashboard`;

  constructor(private http: HttpClient) {}

  getSummary(): Observable<DashboardSummary> {
    return this.http.get<DashboardSummary>(`${this.baseUrl}/summary`);
  }

  getClientDashboard(): Observable<ClientDashboardSummary> {
    return this.http.get<ClientDashboardSummary>(`${this.baseUrl}/client`);
  }
}
