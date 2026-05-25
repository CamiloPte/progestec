import { inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { RoutePersistenceService } from '../services/route-persistence.service';

export const redirectIfAuthenticatedGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);
  const platformId = inject(PLATFORM_ID);
  const routePersistence = inject(RoutePersistenceService);

  if (!isPlatformBrowser(platformId)) {
    return true;
  }

  if (authService.isAuthenticated()) {
    const target = routePersistence.getStoredRoute() ?? '/inicio';
    router.navigateByUrl(target);
    return false;
  }

  return true;
};
