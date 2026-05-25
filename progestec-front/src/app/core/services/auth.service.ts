import { Injectable, Inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { HttpClient, HttpParams, HttpErrorResponse } from '@angular/common/http';
import { Observable, tap, BehaviorSubject, firstValueFrom, catchError, of } from 'rxjs';
import { API_BASE_URL } from '../config/api.config';
import { LoginResponse, SetPasswordRequest, MessageResponse } from '../models/auth';
import { CurrentUser } from '../models/user';

const TOKEN_KEY = 'progestec_token';
const LAST_ROUTE_KEY = 'progestec_last_route';
const MUST_CHANGE_PASSWORD_KEY = 'progestec_must_change_password';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private currentUserSubject = new BehaviorSubject<CurrentUser | null>(null);
  currentUser$ = this.currentUserSubject.asObservable();

  private isBrowserEnv: boolean;

  constructor(
    private http: HttpClient,
    @Inject(PLATFORM_ID) platformId: Object
  ) {
    this.isBrowserEnv = isPlatformBrowser(platformId);
  }

  saveLastRoute(path: string): void {
    if (!this.isBrowser()) {
      return;
    }
    localStorage.setItem(LAST_ROUTE_KEY, path);
  }

  getLastRoute(): string | null {
    if (!this.isBrowser()) {
      return null;
    }
    return localStorage.getItem(LAST_ROUTE_KEY);
  }

  clearLastRoute(): void {
    if (this.isBrowser()) {
      localStorage.removeItem(LAST_ROUTE_KEY);
    }
  }

  // 👇 helper para saber si estamos en navegador
  private isBrowser(): boolean {
    return this.isBrowserEnv && typeof window !== 'undefined' && !!window.localStorage;
  }

  // ---- LOGIN ----
  login(email: string, password: string): Observable<LoginResponse> {
    const body = new HttpParams()
      .set('username', email)   // backend usa email como username
      .set('password', password);

    return this.http
      .post<LoginResponse>(`${API_BASE_URL}/auth/token`, body.toString(), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      })
      .pipe(
        tap((res) => {
          if (res.access_token && this.isBrowser()) {
            localStorage.setItem(TOKEN_KEY, res.access_token);
            // Guardar flag de cambio de contraseña
            if (res.must_change_password) {
              localStorage.setItem(MUST_CHANGE_PASSWORD_KEY, 'true');
            } else {
              localStorage.removeItem(MUST_CHANGE_PASSWORD_KEY);
            }
          }
        })
      );
  }

  // ---- CAMBIO DE CONTRASEÑA ----
  mustChangePassword(): boolean {
    if (!this.isBrowser()) {
      return false;
    }
    return localStorage.getItem(MUST_CHANGE_PASSWORD_KEY) === 'true';
  }

  setPassword(newPassword: string): Observable<MessageResponse> {
    return this.http
      .post<MessageResponse>(`${API_BASE_URL}/auth/set-password`, { new_password: newPassword })
      .pipe(
        tap(() => {
          if (this.isBrowser()) {
            localStorage.removeItem(MUST_CHANGE_PASSWORD_KEY);
          }
        })
      );
  }

  // ---- /auth/me ----
  loadCurrentUser(): Observable<CurrentUser> {
    return this.http
      .get<CurrentUser>(`${API_BASE_URL}/auth/me`)
      .pipe(
        tap((data: any) => {
          const roleName =
            data.role_name ??
            data.role?.name ??
            null;

          const normalized: CurrentUser = {
            id: data.id,
            email: data.email,
            full_name: data.full_name,
            phone: data.phone ?? null,
            role_name: roleName ?? undefined,
            role: data.role ?? undefined,
            modules: data.modules ?? [],
          };

          this.currentUserSubject.next(normalized);
        })
      );
  }

  // Getter sincrónico
  getCurrentUser(): CurrentUser | null {
    return this.currentUserSubject.value;
  }

  // ---- TOKEN ----
  logout(): void {
    if (this.isBrowser()) {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(LAST_ROUTE_KEY);
      localStorage.removeItem(MUST_CHANGE_PASSWORD_KEY);
    }
    this.currentUserSubject.next(null);
  }

  getToken(): string | null {
    if (!this.isBrowser()) {
      return null;
    }
    return localStorage.getItem(TOKEN_KEY);
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  initializeSession(): Promise<void> {
    if (!this.isBrowser()) {
      return Promise.resolve();
    }

    const token = this.getToken();
    if (!token) {
      localStorage.removeItem(LAST_ROUTE_KEY);
      return Promise.resolve();
    }

    return firstValueFrom(
      this.loadCurrentUser().pipe(
        catchError((err: unknown) => {
          console.warn('No se pudo restaurar la sesión automáticamente', err);
          if (err instanceof HttpErrorResponse && err.status === 401) {
            this.logout();
          }
          return of(null);
        })
      )
    ).then(() => {});
  }
}

export function initializeAuth(authService: AuthService): () => Promise<void> {
  return () => authService.initializeSession();
}
