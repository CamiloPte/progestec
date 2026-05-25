// src/app/client-portal/client-devices/client-devices.component.ts
import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { Router } from '@angular/router';
import { DashboardService } from '../../core/services/dashboard.service';
import { ClientDeviceSummary } from '../../core/models/dashboard';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner.component';

@Component({
  selector: 'app-client-devices',
  standalone: true,
  imports: [CommonModule, LoadingSpinnerComponent],
  template: `
    <div class="client-page">
      <header class="page-header">
        <button class="btn-back" (click)="goBack()">
          <span class="back-icon">←</span> Volver
        </button>
        <h1>📱 Mis Dispositivos</h1>
      </header>

      @if (loading) {
        <div class="loading-section">
          <app-loading-spinner 
            type="helix" 
            color="primary" 
            message="Cargando tus dispositivos...">
          </app-loading-spinner>
        </div>
      } @else if (devices.length === 0) {
        <div class="empty-state fade-in">
          <span class="empty-icon">📦</span>
          <h3>Sin dispositivos</h3>
          <p>No tienes dispositivos registrados aún.</p>
          <p class="hint">Los dispositivos se registran cuando llevas un equipo al servicio técnico.</p>
        </div>
      } @else {
        <div class="devices-grid fade-in">
          @for (device of devices; track device.id) {
            <div class="device-card" (click)="viewDevice(device.id)">
              <div class="device-icon-wrapper">
                <span class="device-icon">{{ getDeviceIcon(device.type) }}</span>
              </div>
              <div class="device-info">
                <h3>{{ device.brand }} {{ device.model }}</h3>
                <span class="device-type">{{ getTypeName(device.type) }}</span>
                @if (device.serial) {
                  <p class="device-serial">
                    <span class="label">Serial:</span> {{ device.serial }}
                  </p>
                }
              </div>
              <div class="device-footer">
                <div class="stat">
                  <span class="stat-value">{{ device.tickets_count }}</span>
                  <span class="stat-label">Servicios</span>
                </div>
                @if (device.last_service_status) {
                  <div class="last-service">
                    <span class="service-label">Último estado:</span>
                    <span class="service-status" [class]="getStatusClass(device.last_service_status)">
                      {{ device.last_service_status }}
                    </span>
                  </div>
                }
              </div>
              <span class="card-arrow">→</span>
            </div>
          }
        </div>
      }
    </div>
  `,
  styles: [`
    .client-page {
      min-height: 100vh;
      background: var(--gradient-background, linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%));
      padding: 1.5rem;
    }

    .page-header {
      display: flex;
      align-items: center;
      gap: 1rem;
      margin-bottom: 1.5rem;
      max-width: 1200px;
      margin-left: auto;
      margin-right: auto;
    }

    .btn-back {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      background: var(--color-white, white);
      border: 1px solid var(--color-gray-300, #ddd);
      padding: 0.5rem 1rem;
      border-radius: var(--radius, 8px);
      cursor: pointer;
      font-weight: 500;
      color: var(--color-gray-700, #333);
      transition: all var(--transition, 0.2s);
    }

    .btn-back:hover {
      background: var(--color-primary, #1a5c3a);
      color: white;
      border-color: var(--color-primary, #1a5c3a);
    }

    .page-header h1 {
      margin: 0;
      color: var(--color-primary, #1a5c3a);
      font-size: 1.5rem;
    }

    .loading-section {
      max-width: 1200px;
      margin: 0 auto;
      padding: 3rem;
      background: var(--color-white, white);
      border-radius: var(--radius-lg, 12px);
    }

    .empty-state {
      text-align: center;
      padding: 3rem;
      background: var(--color-white, white);
      border-radius: var(--radius-lg, 12px);
      max-width: 500px;
      margin: 0 auto;
      box-shadow: var(--shadow, 0 2px 8px rgba(0,0,0,0.06));
    }

    .empty-icon {
      font-size: 4rem;
      display: block;
      margin-bottom: 1rem;
    }

    .empty-state h3 {
      color: var(--color-gray-800, #333);
      margin: 0 0 0.5rem;
    }

    .empty-state p {
      color: var(--color-gray-600, #666);
      margin: 0;
    }

    .empty-state .hint {
      margin-top: 1rem;
      font-size: 0.85rem;
      color: var(--color-gray-500, #888);
    }

    .devices-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 1.25rem;
      max-width: 1200px;
      margin: 0 auto;
    }

    .device-card {
      background: var(--color-white, white);
      border-radius: var(--radius-lg, 12px);
      padding: 1.5rem;
      box-shadow: var(--shadow, 0 2px 8px rgba(0,0,0,0.06));
      display: flex;
      flex-direction: column;
      gap: 1rem;
      cursor: pointer;
      transition: all var(--transition, 0.2s);
      position: relative;
      border: 2px solid transparent;
    }

    .device-card:hover {
      transform: translateY(-4px);
      box-shadow: var(--shadow-lg, 0 10px 25px rgba(0,0,0,0.15));
      border-color: var(--color-primary, #1a5c3a);
    }

    .device-icon-wrapper {
      display: flex;
      justify-content: center;
    }

    .device-icon {
      font-size: 3.5rem;
      background: var(--color-primary-50, #e8f5ed);
      padding: 1rem 1.5rem;
      border-radius: var(--radius-lg, 12px);
    }

    .device-info {
      text-align: center;
    }

    .device-info h3 {
      margin: 0 0 0.25rem;
      color: var(--color-gray-800, #333);
      font-size: 1.15rem;
    }

    .device-type {
      display: inline-block;
      background: var(--color-secondary-100, #fbf0cc);
      color: var(--color-secondary-dark, #a8871e);
      padding: 0.2rem 0.6rem;
      border-radius: var(--radius-full, 20px);
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
    }

    .device-serial {
      font-size: 0.85rem;
      color: var(--color-gray-500, #999);
      margin: 0.5rem 0 0;
      font-family: monospace;
    }

    .device-serial .label {
      color: var(--color-gray-400, #aaa);
    }

    .device-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 1rem;
      border-top: 1px solid var(--color-gray-200, #eee);
    }

    .stat {
      display: flex;
      flex-direction: column;
      align-items: center;
    }

    .stat-value {
      font-size: 1.5rem;
      font-weight: 700;
      color: var(--color-primary, #1a5c3a);
    }

    .stat-label {
      font-size: 0.75rem;
      color: var(--color-gray-500, #999);
    }

    .last-service {
      text-align: right;
    }

    .service-label {
      display: block;
      font-size: 0.7rem;
      color: var(--color-gray-400, #aaa);
      text-transform: uppercase;
    }

    .service-status {
      font-weight: 600;
      font-size: 0.85rem;
      color: var(--color-gray-700, #333);
    }

    .service-status.status-success {
      color: var(--color-success, #27ae60);
    }

    .service-status.status-warning {
      color: var(--color-warning, #f39c12);
    }

    .service-status.status-info {
      color: var(--color-info, #3498db);
    }

    .card-arrow {
      position: absolute;
      top: 1rem;
      right: 1rem;
      font-size: 1.25rem;
      color: var(--color-primary, #1a5c3a);
      opacity: 0;
      transition: opacity var(--transition, 0.2s);
    }

    .device-card:hover .card-arrow {
      opacity: 1;
    }

    /* Animations */
    .fade-in {
      animation: fadeIn 0.3s ease-out;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }

    /* Responsive */
    @media (max-width: 768px) {
      .client-page {
        padding: 1rem;
      }

      .devices-grid {
        grid-template-columns: 1fr;
      }

      .device-icon {
        font-size: 2.5rem;
        padding: 0.75rem 1rem;
      }
    }
  `]
})
export class ClientDevicesComponent implements OnInit {
  devices: ClientDeviceSummary[] = [];
  loading = true;
  isBrowser: boolean;

  constructor(
    private dashboardService: DashboardService,
    private router: Router,
    @Inject(PLATFORM_ID) platformId: object
  ) {
    this.isBrowser = isPlatformBrowser(platformId);
  }

  ngOnInit(): void {
    if (this.isBrowser) {
      this.loadDevices();
    }
  }

  loadDevices(): void {
    this.dashboardService.getClientDashboard().subscribe({
      next: (data) => {
        this.devices = data.devices;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    });
  }

  goBack(): void {
    this.router.navigate(['/client/dashboard']);
  }

  viewDevice(deviceId: number): void {
    this.router.navigate(['/client/devices', deviceId]);
  }

  getDeviceIcon(type: string): string {
    const icons: Record<string, string> = {
      'PHONE': '📱', 'LAPTOP': '💻', 'TABLET': '📟', 'OTHER': '🔧'
    };
    return icons[type?.toUpperCase()] || '📦';
  }

  getTypeName(type: string): string {
    const names: Record<string, string> = {
      'PHONE': 'Teléfono', 'LAPTOP': 'Laptop', 'TABLET': 'Tablet', 'OTHER': 'Otro'
    };
    return names[type?.toUpperCase()] || type;
  }

  getStatusClass(status: string): string {
    const lower = status?.toLowerCase() || '';
    if (lower.includes('cerrado') || lower.includes('entregado') || lower.includes('listo')) {
      return 'status-success';
    }
    if (lower.includes('esperando') || lower.includes('aprobación')) {
      return 'status-warning';
    }
    return 'status-info';
  }
}
