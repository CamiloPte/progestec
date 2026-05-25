import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { Observable, Subscription } from 'rxjs';

import { AuthService } from '../services/auth.service';
import { CurrentUser } from '../models/user';
import { PermissionService } from '../services/permission.service';
import { IdleService } from '../services/idle.service';

interface SidebarLink {
  label: string;
  path?: string;
  icon: string;
  disabled?: boolean;
  implemented?: boolean;
}

const MODULE_LINKS: Record<string, SidebarLink> = {
  DASHBOARD: { label: 'Dashboard', path: '/inicio', icon: 'DB', implemented: true },
  TICKETS: { label: 'Tickets', path: '/tickets', icon: 'TK', implemented: true },
  USERS: { label: 'Usuarios', path: '/usuarios', icon: 'US', implemented: true },
  DEVICES: { label: 'Dispositivos', path: '/dispositivos', icon: 'DV', implemented: false },
  INVENTORY: { label: 'Inventario', path: '/inventario', icon: 'IV', implemented: true },
  REPORTS: { label: 'Reportes', path: '/reportes', icon: 'RP', implemented: false },
  FINANCE: { label: 'Finanzas', path: '/finanzas', icon: 'FN', implemented: true },
};

@Component({
  selector: 'app-authenticated-layout',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './authenticated-layout.component.html',
  styleUrls: ['./authenticated-layout.component.css'],
})
export class AuthenticatedLayoutComponent {
  user$: Observable<CurrentUser | null>;
  currentYear = new Date().getFullYear();
  links: SidebarLink[] = [];
  showIdleModal = false;
  private subs = new Subscription();

  constructor(
    private authService: AuthService,
    private permissionService: PermissionService,
    private idleService: IdleService,
    private router: Router
  ) {
    this.user$ = this.authService.currentUser$;
    this.user$.subscribe((user) => {
      this.links = this.buildLinks(user);
    });

    const idleSub = this.idleService.warningState$.subscribe((warn) => {
      if (warn) {
        this.showIdleModal = true;
      } else {
        this.showIdleModal = false;
      }
    });
    this.subs.add(idleSub);
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  stayActive(): void {
    this.idleService.resetTimers();
    this.showIdleModal = false;
  }

  getUserInitial(user: CurrentUser | null): string {
    const source = user?.full_name || user?.email || '';
    return source.trim().charAt(0).toUpperCase();
  }

  private buildLinks(user: CurrentUser | null): SidebarLink[] {
    const modules = user?.modules ?? [];
    if (!modules.length) {
      return [MODULE_LINKS['DASHBOARD']];
    }
    return modules
      .map((name) => MODULE_LINKS[name])
      .filter((link): link is SidebarLink => !!link)
      .map((link) => ({
        ...link,
        disabled: !link.implemented,
      }));
  }

  ngOnDestroy(): void {
    this.subs.unsubscribe();
    this.idleService.stop();
  }
}
