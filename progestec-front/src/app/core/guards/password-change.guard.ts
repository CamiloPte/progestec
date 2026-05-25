import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

/**
 * Guard que verifica si el usuario debe cambiar su contraseña.
 * Si must_change_password es true, redirige a /change-password
 */
export const mustChangePasswordGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  // Si el usuario debe cambiar contraseña, redirigir
  if (authService.mustChangePassword()) {
    router.navigate(['/change-password']);
    return false;
  }

  return true;
};

/**
 * Guard que permite acceso SOLO si el usuario debe cambiar contraseña.
 * Usado para proteger la ruta /change-password
 */
export const requirePasswordChangeGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  // Solo permitir acceso si debe cambiar contraseña
  if (!authService.mustChangePassword()) {
    // Si no necesita cambiar, redirigir al inicio
    const user = authService.getCurrentUser();
    if (user?.role_name === 'CLIENT') {
      router.navigate(['/client']);
    } else {
      router.navigate(['/inicio']);
    }
    return false;
  }

  return true;
};
