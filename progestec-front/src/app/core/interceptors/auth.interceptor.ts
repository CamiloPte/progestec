import { Injectable } from '@angular/core';
import {
  HttpInterceptor,
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpErrorResponse,
} from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';
import { API_BASE_URL } from '../config/api.config';
import { Router } from '@angular/router';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  private handling401 = false;

  constructor(private authService: AuthService, private router: Router) {}

  intercept(
    request: HttpRequest<unknown>,
    next: HttpHandler
  ): Observable<HttpEvent<unknown>> {
    const token = this.authService.getToken();
    const isApiRequest = request.url.startsWith(API_BASE_URL);
    let outgoing = request;

    if (token && isApiRequest) {
      outgoing = request.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`,
        },
      });
    }

    return next.handle(outgoing).pipe(
      catchError((error: HttpErrorResponse) => {
        if (
          isApiRequest &&
          error.status === 401 &&
          !this.handling401 &&
          !request.url.includes('/auth/token') &&
          !request.url.includes('/auth/login')
        ) {
          this.handling401 = true;
          this.authService.logout();
          this.router.navigate(['/login']).finally(() => {
            this.handling401 = false;
          });
        }
        return throwError(() => error);
      })
    );
  }
}
