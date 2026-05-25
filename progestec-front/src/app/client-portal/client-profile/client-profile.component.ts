// src/app/client-portal/client-profile/client-profile.component.ts
import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { CurrentUser } from '../../core/models/user';

@Component({
  selector: 'app-client-profile',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="client-page">
      <header class="page-header">
        <button class="btn-back" (click)="goBack()">← Volver</button>
        <h1>👤 Mi Perfil</h1>
      </header>

      @if (user) {
        <div class="profile-card">
          <div class="avatar">
            <span>{{ getInitials() }}</span>
          </div>
          <h2>{{ user.full_name }}</h2>
          <p class="email">{{ user.email }}</p>
        </div>

        <div class="info-card">
          <h3>Información personal</h3>
          <div class="info-grid">
            <div class="info-item">
              <span class="label">Nombre completo</span>
              <span class="value">{{ user.full_name || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="label">Email</span>
              <span class="value">{{ user.email }}</span>
            </div>
            <div class="info-item">
              <span class="label">Teléfono</span>
              <span class="value">{{ user.phone || 'No registrado' }}</span>
            </div>
            <div class="info-item">
              <span class="label">Identificación</span>
              <span class="value">{{ user.identification || 'No registrada' }}</span>
            </div>
          </div>
        </div>

        <div class="info-card">
          <h3>Seguridad</h3>
          <p class="security-text">Para cambiar tu contraseña o actualizar tus datos, contacta a nuestro equipo de soporte.</p>
          <div class="contact-info">
            <p>📞 +57 301 255-4106</p>
            <p>✉️ servicioprogestec&#64;gmail.com</p>
          </div>
        </div>

        <div class="actions">
          <button class="btn-logout" (click)="logout()">
            Cerrar sesión
          </button>
        </div>
      }
    </div>
  `,
  styles: [`
    .client-page { min-height: 100vh; background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%); padding: 1.5rem; max-width: 600px; margin: 0 auto; }
    .page-header { display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem; }
    .btn-back { background: white; border: 1px solid #ddd; padding: 0.5rem 1rem; border-radius: 8px; cursor: pointer; }
    .page-header h1 { margin: 0; color: #1a5c3a; font-size: 1.5rem; }
    .profile-card { text-align: center; background: white; border-radius: 16px; padding: 2rem; margin-bottom: 1rem; box-shadow: 0 2px 10px rgba(0,0,0,0.06); }
    .avatar { width: 80px; height: 80px; border-radius: 50%; background: linear-gradient(135deg, #1a5c3a 0%, #2d8659 100%); color: white; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem; font-size: 2rem; font-weight: 700; }
    .profile-card h2 { margin: 0; color: #333; }
    .profile-card .email { color: #666; margin: 0.25rem 0 0; }
    .info-card { background: white; border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
    .info-card h3 { margin: 0 0 1rem; color: #333; font-size: 1.1rem; }
    .info-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; }
    .info-item .label { display: block; font-size: 0.8rem; color: #999; margin-bottom: 0.25rem; }
    .info-item .value { color: #333; font-weight: 500; }
    .security-text { color: #666; margin: 0 0 1rem; }
    .contact-info { background: #f8f9fa; padding: 1rem; border-radius: 8px; }
    .contact-info p { margin: 0.25rem 0; color: #333; }
    .actions { margin-top: 2rem; text-align: center; }
    .btn-logout { background: #e74c3c; color: white; border: none; padding: 0.75rem 2rem; border-radius: 8px; cursor: pointer; font-size: 1rem; }
    .btn-logout:hover { background: #c0392b; }
    @media (max-width: 500px) { .info-grid { grid-template-columns: 1fr; } }
  `]
})
export class ClientProfileComponent implements OnInit {
  user: CurrentUser | null = null;
  isBrowser: boolean;

  constructor(
    private authService: AuthService,
    private router: Router,
    @Inject(PLATFORM_ID) platformId: object
  ) {
    this.isBrowser = isPlatformBrowser(platformId);
  }

  ngOnInit(): void {
    if (this.isBrowser) {
      this.authService.currentUser$.subscribe(u => this.user = u);
    }
  }

  goBack(): void {
    this.router.navigate(['/client/dashboard']);
  }

  getInitials(): string {
    if (!this.user?.full_name) return '?';
    const parts = this.user.full_name.split(' ');
    return parts.map(p => p[0]).slice(0, 2).join('').toUpperCase();
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
