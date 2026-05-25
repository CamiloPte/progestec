import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import { API_BASE_URL } from '../config/api.config';
import { UserReadMinimal, UserReadDetail, UserCreate, UserUpdate } from '../models/user';

@Injectable({
  providedIn: 'root',
})
export class UserService {
  private readonly baseUrl = `${API_BASE_URL}/users`;

  constructor(private http: HttpClient) {}

  /**
   * Listar todos los usuarios con filtros opcionales
   */
  listUsers(params?: { role?: string; search?: string }): Observable<UserReadMinimal[]> {
    let httpParams = new HttpParams();
    if (params?.role) {
      httpParams = httpParams.set('role', params.role);
    }
    if (params?.search) {
      httpParams = httpParams.set('search', params.search);
    }
    return this.http.get<UserReadMinimal[]>(this.baseUrl, { params: httpParams });
  }

  /**
   * Obtener detalle de un usuario
   */
  getUserById(userId: number): Observable<UserReadDetail> {
    return this.http.get<UserReadDetail>(`${this.baseUrl}/${userId}`);
  }

  /**
   * Crear un nuevo usuario
   */
  createUser(data: UserCreate): Observable<UserReadDetail> {
    return this.http.post<UserReadDetail>(this.baseUrl, data);
  }

  /**
   * Actualizar un usuario
   */
  updateUser(userId: number, data: UserUpdate): Observable<UserReadDetail> {
    return this.http.put<UserReadDetail>(`${this.baseUrl}/${userId}`, data);
  }

  /**
   * Cambiar el rol de un usuario
   */
  changeUserRole(userId: number, roleId: number): Observable<UserReadDetail> {
    return this.http.patch<UserReadDetail>(`${this.baseUrl}/${userId}/role`, { role_id: roleId });
  }

  /**
   * Cambiar el estado de un usuario (activar/desactivar)
   */
  changeUserState(userId: number, state: number): Observable<UserReadDetail> {
    return this.http.patch<UserReadDetail>(`${this.baseUrl}/${userId}/state`, { state });
  }

  /**
   * Listar técnicos activos
   */
  listTechnicians(): Observable<UserReadMinimal[]> {
    return this.http.get<UserReadMinimal[]>(`${this.baseUrl}/technicians`);
  }

  /**
   * Listar clientes activos
   */
  listClients(): Observable<UserReadMinimal[]> {
    return this.http.get<UserReadMinimal[]>(`${this.baseUrl}/clients`);
  }

  /**
   * Crear cliente rápidamente (desde flujo de tickets)
   */
  quickCreateClient(payload: {
    full_name: string;
    email: string;
    identification: string;
    identification_type?: string | null;
    phone?: string | null;
  }): Observable<UserReadMinimal> {
    return this.http.post<UserReadMinimal>(`${this.baseUrl}/clients/quick`, payload);
  }
}
