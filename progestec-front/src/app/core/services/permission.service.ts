import { Injectable } from '@angular/core';

import { CurrentUser } from '../models/user';

@Injectable({ providedIn: 'root' })
export class PermissionService {
  canAccessModule(user: CurrentUser | null, moduleName: string): boolean {
    const modules = user?.modules ?? [];
    return modules.map((m) => m.toUpperCase()).includes(moduleName.toUpperCase());
  }

  canCreateTicket(user: CurrentUser | null): boolean {
    const role = (user?.role_name || '').toUpperCase();
    return role === 'ADMIN' || role === 'ADVISOR';
  }

  canManageFinance(user: CurrentUser | null): boolean {
    return this.canAccessModule(user, 'FINANCE');
  }

  canViewInventory(user: CurrentUser | null): boolean {
    return this.canAccessModule(user, 'INVENTORY');
  }

  canManageUsers(user: CurrentUser | null): boolean {
    // Solo ADMIN puede gestionar usuarios
    return this.isAdmin(user);
  }

  isTechnician(user: CurrentUser | null): boolean {
    return (user?.role_name || '').toUpperCase() === 'TECHNICIAN';
  }

  isAdvisor(user: CurrentUser | null): boolean {
    return (user?.role_name || '').toUpperCase() === 'ADVISOR';
  }

  isAdmin(user: CurrentUser | null): boolean {
    return (user?.role_name || '').toUpperCase() === 'ADMIN';
  }

  isClient(user: CurrentUser | null): boolean {
    return (user?.role_name || '').toUpperCase() === 'CLIENT';
  }
}
