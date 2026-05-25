import { inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { CanActivateFn, Router } from '@angular/router';
import { map, take, filter } from 'rxjs/operators';

import { AuthService } from '../services/auth.service';
import { PermissionService } from '../services/permission.service';
import { CurrentUser } from '../models/user';

export const financeGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const permissionService = inject(PermissionService);
  const router = inject(Router);
  const platformId = inject(PLATFORM_ID);

  if (!isPlatformBrowser(platformId)) {
    return true;
  }

  if (!authService.isAuthenticated()) {
    router.navigate(['/login']);
    return false;
  }

  // Esperar a que el usuario esté cargado
  return authService.currentUser$.pipe(
    filter((user): user is CurrentUser => user !== null),
    take(1),
    map((user) => {
      if (permissionService.canManageFinance(user)) {
        return true;
      }
      router.navigate(['/inicio']);
      return false;
    })
  );
};
