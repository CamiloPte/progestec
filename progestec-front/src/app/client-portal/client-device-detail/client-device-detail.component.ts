// src/app/client-portal/client-device-detail/client-device-detail.component.ts
import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { Router, ActivatedRoute } from '@angular/router';
import { DashboardService } from '../../core/services/dashboard.service';
import { TicketService } from '../../core/services/ticket.service';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner.component';
import { ClientDeviceSummary } from '../../core/models/dashboard';
import { TicketReadMinimal } from '../../core/models/ticket';

interface TicketHistory {
  id: number;
  tracking_code: string;
  failure_desc: string;
  created_at: string;
  closed_at?: string;
  status: { name: string; code: string; color?: string };
}

@Component({
  selector: 'app-client-device-detail',
  standalone: true,
  imports: [CommonModule, LoadingSpinnerComponent],
  template: `
    <div class="client-page">
      <header class="page-header">
        <button class="btn-back" (click)="goBack()">
          <span class="back-icon">←</span> Volver
        </button>
        <h1>
          @if (device) {
            <span class="device-icon">{{ getDeviceIcon(device.type) }}</span>
            {{ device.brand }} {{ device.model }}
          } @else {
            Detalle del Dispositivo
          }
        </h1>
      </header>

      @if (loading) {
        <div class="loading-section">
          <app-loading-spinner 
            type="helix" 
            color="primary" 
            message="Cargando información del dispositivo...">
          </app-loading-spinner>
        </div>
      } @else if (error) {
        <div class="error-card">
          <span class="error-icon">⚠️</span>
          <h3>Error al cargar</h3>
          <p>{{ error }}</p>
          <button class="btn btn-primary" (click)="loadDevice()">Reintentar</button>
        </div>
      } @else if (device) {
        <div class="device-layout fade-in">
          <!-- Información Principal -->
          <section class="device-info-card">
            <div class="device-header">
              <div class="device-main-icon">{{ getDeviceIcon(device.type) }}</div>
              <div class="device-title">
                <h2>{{ device.brand }} {{ device.model }}</h2>
                <span class="device-type-badge">{{ getTypeName(device.type) }}</span>
              </div>
            </div>

            <div class="device-specs">
              <div class="spec-group">
                <h4>📋 Especificaciones</h4>
                <div class="spec-list">
                  <div class="spec-item">
                    <span class="spec-label">Tipo</span>
                    <span class="spec-value">{{ getTypeName(device.type) }}</span>
                  </div>
                  <div class="spec-item">
                    <span class="spec-label">Marca</span>
                    <span class="spec-value">{{ device.brand }}</span>
                  </div>
                  <div class="spec-item">
                    <span class="spec-label">Modelo</span>
                    <span class="spec-value">{{ device.model }}</span>
                  </div>
                  @if (device.serial) {
                    <div class="spec-item">
                      <span class="spec-label">Serial</span>
                      <span class="spec-value code">{{ device.serial }}</span>
                    </div>
                  }
                  @if (device.last_service_date) {
                    <div class="spec-item">
                      <span class="spec-label">Último servicio</span>
                      <span class="spec-value">{{ device.last_service_date | date:'dd/MM/yyyy' }}</span>
                    </div>
                  }
                </div>
              </div>
            </div>
          </section>

          <!-- Historial de Servicios -->
          <section class="service-history-card">
            <div class="section-header">
              <h3>🔧 Historial de Servicios</h3>
              <span class="services-count">{{ tickets.length }} servicio(s)</span>
            </div>

            @if (loadingTickets) {
              <div class="loading-inline">
                <app-loading-spinner type="bouncy" color="secondary"></app-loading-spinner>
              </div>
            } @else if (tickets.length === 0) {
              <div class="empty-history">
                <span class="empty-icon">✨</span>
                <h4>Sin historial de servicios</h4>
                <p>Este dispositivo no ha tenido servicios técnicos registrados.</p>
              </div>
            } @else {
              <div class="timeline">
                @for (ticket of tickets; track ticket.id) {
                  <div class="timeline-item" (click)="viewTicket(ticket.id)">
                    <div class="timeline-marker" [style.background]="ticket.status.color || '#1a5c3a'"></div>
                    <div class="timeline-content">
                      <div class="timeline-header">
                        <span class="ticket-code">{{ ticket.tracking_code }}</span>
                        <span class="status-badge" 
                              [style.background]="(ticket.status.color || '#1a5c3a') + '20'"
                              [style.color]="ticket.status.color || '#1a5c3a'">
                          {{ ticket.status.name }}
                        </span>
                      </div>
                      <p class="ticket-problem">{{ ticket.failure_desc }}</p>
                      <div class="timeline-dates">
                        <span class="date-item">
                          <span class="date-icon">📅</span>
                          Ingreso: {{ ticket.created_at | date:'dd/MM/yyyy' }}
                        </span>
                        @if (ticket.closed_at) {
                          <span class="date-item">
                            <span class="date-icon">✅</span>
                            Cerrado: {{ ticket.closed_at | date:'dd/MM/yyyy' }}
                          </span>
                        }
                      </div>
                    </div>
                    <span class="timeline-arrow">→</span>
                  </div>
                }
              </div>
            }
          </section>

          <!-- Resumen Rápido -->
          <section class="quick-stats-card">
            <h3>📊 Resumen</h3>
            <div class="stats-grid">
              <div class="stat-item">
                <span class="stat-icon">🔧</span>
                <div class="stat-info">
                  <span class="stat-number">{{ tickets.length }}</span>
                  <span class="stat-label">Servicios totales</span>
                </div>
              </div>
              <div class="stat-item">
                <span class="stat-icon">✅</span>
                <div class="stat-info">
                  <span class="stat-number">{{ getCompletedCount() }}</span>
                  <span class="stat-label">Completados</span>
                </div>
              </div>
              <div class="stat-item">
                <span class="stat-icon">⏳</span>
                <div class="stat-info">
                  <span class="stat-number">{{ getActiveCount() }}</span>
                  <span class="stat-label">Activos</span>
                </div>
              </div>
            </div>
          </section>
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
      max-width: 1000px;
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
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .device-icon {
      font-size: 1.75rem;
    }

    .loading-section, .error-card {
      max-width: 1000px;
      margin: 0 auto;
      padding: 3rem;
      background: var(--color-white, white);
      border-radius: var(--radius-lg, 12px);
      text-align: center;
    }

    .error-card {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 1rem;
    }

    .error-icon {
      font-size: 3rem;
    }

    .error-card h3 {
      margin: 0;
      color: var(--color-danger, #e74c3c);
    }

    .error-card p {
      color: var(--color-gray-600, #666);
      margin: 0;
    }

    /* Device Layout */
    .device-layout {
      max-width: 1000px;
      margin: 0 auto;
      display: grid;
      gap: 1.5rem;
      grid-template-columns: 1fr 1fr;
    }

    /* Device Info Card */
    .device-info-card {
      background: var(--color-white, white);
      border-radius: var(--radius-lg, 12px);
      padding: 1.5rem;
      box-shadow: var(--shadow, 0 2px 8px rgba(0,0,0,0.06));
      grid-column: 1 / 2;
    }

    .device-header {
      display: flex;
      align-items: center;
      gap: 1rem;
      padding-bottom: 1.5rem;
      border-bottom: 2px solid var(--color-primary-50, #e8f5ed);
      margin-bottom: 1.5rem;
    }

    .device-main-icon {
      font-size: 3.5rem;
      background: var(--color-primary-50, #e8f5ed);
      padding: 1rem;
      border-radius: var(--radius-lg, 12px);
    }

    .device-title h2 {
      margin: 0 0 0.5rem;
      color: var(--color-gray-800, #1f2937);
    }

    .device-type-badge {
      display: inline-block;
      background: var(--color-secondary-100, #fbf0cc);
      color: var(--color-secondary-dark, #a8871e);
      padding: 0.25rem 0.75rem;
      border-radius: var(--radius-full, 20px);
      font-size: 0.8rem;
      font-weight: 600;
    }

    .spec-group {
      margin-bottom: 1.5rem;
    }

    .spec-group:last-child {
      margin-bottom: 0;
    }

    .spec-group h4 {
      color: var(--color-primary, #1a5c3a);
      margin: 0 0 1rem;
      font-size: 1rem;
    }

    .spec-list {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }

    .spec-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.5rem 0;
      border-bottom: 1px solid var(--color-gray-100, #f0f0f0);
    }

    .spec-item:last-child {
      border-bottom: none;
    }

    .spec-label {
      color: var(--color-gray-500, #6b7280);
      font-size: 0.9rem;
    }

    .spec-value {
      color: var(--color-gray-800, #1f2937);
      font-weight: 500;
    }

    .spec-value.code {
      font-family: monospace;
      background: var(--color-gray-100, #f5f5f5);
      padding: 0.25rem 0.5rem;
      border-radius: 4px;
      font-size: 0.85rem;
    }

    .device-notes {
      color: var(--color-gray-600, #4b5563);
      line-height: 1.6;
      margin: 0;
      background: var(--color-gray-50, #f9fafb);
      padding: 1rem;
      border-radius: var(--radius, 8px);
    }

    /* Service History */
    .service-history-card {
      background: var(--color-white, white);
      border-radius: var(--radius-lg, 12px);
      padding: 1.5rem;
      box-shadow: var(--shadow, 0 2px 8px rgba(0,0,0,0.06));
      grid-column: 2 / 3;
      grid-row: 1 / 3;
    }

    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.5rem;
    }

    .section-header h3 {
      margin: 0;
      color: var(--color-gray-800, #1f2937);
    }

    .services-count {
      background: var(--color-primary-50, #e8f5ed);
      color: var(--color-primary, #1a5c3a);
      padding: 0.25rem 0.75rem;
      border-radius: var(--radius-full, 20px);
      font-size: 0.85rem;
      font-weight: 600;
    }

    .loading-inline {
      padding: 2rem;
    }

    .empty-history {
      text-align: center;
      padding: 2rem;
      background: var(--color-gray-50, #f9fafb);
      border-radius: var(--radius, 8px);
    }

    .empty-icon {
      font-size: 3rem;
      display: block;
      margin-bottom: 0.5rem;
    }

    .empty-history h4 {
      margin: 0 0 0.5rem;
      color: var(--color-gray-700, #374151);
    }

    .empty-history p {
      margin: 0;
      color: var(--color-gray-500, #6b7280);
    }

    /* Timeline */
    .timeline {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .timeline-item {
      display: flex;
      align-items: flex-start;
      gap: 1rem;
      padding: 1rem;
      background: var(--color-gray-50, #f9fafb);
      border-radius: var(--radius, 8px);
      cursor: pointer;
      transition: all var(--transition, 0.2s);
      border: 2px solid transparent;
    }

    .timeline-item:hover {
      background: var(--color-white, white);
      border-color: var(--color-primary, #1a5c3a);
      box-shadow: var(--shadow-md, 0 4px 12px rgba(0,0,0,0.1));
    }

    .timeline-marker {
      width: 12px;
      height: 12px;
      border-radius: 50%;
      margin-top: 4px;
      flex-shrink: 0;
    }

    .timeline-content {
      flex: 1;
    }

    .timeline-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.5rem;
      flex-wrap: wrap;
      gap: 0.5rem;
    }

    .ticket-code {
      font-weight: 700;
      color: var(--color-primary, #1a5c3a);
      font-size: 0.95rem;
    }

    .status-badge {
      padding: 0.2rem 0.6rem;
      border-radius: var(--radius-full, 20px);
      font-size: 0.75rem;
      font-weight: 600;
    }

    .ticket-problem {
      margin: 0 0 0.5rem;
      color: var(--color-gray-600, #4b5563);
      font-size: 0.9rem;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .timeline-dates {
      display: flex;
      gap: 1rem;
      flex-wrap: wrap;
    }

    .date-item {
      display: flex;
      align-items: center;
      gap: 0.25rem;
      font-size: 0.8rem;
      color: var(--color-gray-500, #6b7280);
    }

    .date-icon {
      font-size: 0.9rem;
    }

    .timeline-arrow {
      color: var(--color-primary, #1a5c3a);
      font-size: 1.25rem;
      opacity: 0;
      transition: opacity var(--transition, 0.2s);
    }

    .timeline-item:hover .timeline-arrow {
      opacity: 1;
    }

    /* Quick Stats */
    .quick-stats-card {
      background: var(--color-white, white);
      border-radius: var(--radius-lg, 12px);
      padding: 1.5rem;
      box-shadow: var(--shadow, 0 2px 8px rgba(0,0,0,0.06));
      grid-column: 1 / 2;
    }

    .quick-stats-card h3 {
      margin: 0 0 1rem;
      color: var(--color-gray-800, #1f2937);
    }

    .stats-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 1rem;
    }

    .stat-item {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 0.75rem;
      background: var(--color-gray-50, #f9fafb);
      border-radius: var(--radius, 8px);
    }

    .stat-icon {
      font-size: 1.5rem;
    }

    .stat-info {
      display: flex;
      flex-direction: column;
    }

    .stat-number {
      font-size: 1.25rem;
      font-weight: 700;
      color: var(--color-primary, #1a5c3a);
    }

    .stat-label {
      font-size: 0.75rem;
      color: var(--color-gray-500, #6b7280);
    }

    /* Buttons */
    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      padding: 0.6rem 1.2rem;
      border-radius: var(--radius, 8px);
      font-weight: 500;
      cursor: pointer;
      border: none;
      transition: all var(--transition, 0.2s);
    }

    .btn-primary {
      background: var(--color-primary, #1a5c3a);
      color: white;
    }

    .btn-primary:hover {
      background: var(--color-primary-dark, #155230);
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
    @media (max-width: 900px) {
      .device-layout {
        grid-template-columns: 1fr;
      }

      .device-info-card,
      .service-history-card,
      .quick-stats-card {
        grid-column: 1 / -1;
        grid-row: auto;
      }

      .stats-grid {
        grid-template-columns: repeat(3, 1fr);
      }
    }

    @media (max-width: 600px) {
      .client-page {
        padding: 1rem;
      }

      .page-header {
        flex-wrap: wrap;
      }

      .device-header {
        flex-direction: column;
        text-align: center;
      }

      .stats-grid {
        grid-template-columns: 1fr;
      }

      .timeline-dates {
        flex-direction: column;
        gap: 0.25rem;
      }
    }
  `]
})
export class ClientDeviceDetailComponent implements OnInit {
  device: ClientDeviceSummary | null = null;
  tickets: TicketHistory[] = [];
  loading = true;
  loadingTickets = false;
  error: string | null = null;
  isBrowser: boolean;
  deviceId: number | null = null;

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private dashboardService: DashboardService,
    private ticketService: TicketService,
    @Inject(PLATFORM_ID) platformId: object
  ) {
    this.isBrowser = isPlatformBrowser(platformId);
  }

  ngOnInit(): void {
    if (this.isBrowser) {
      this.route.params.subscribe(params => {
        this.deviceId = +params['id'];
        if (this.deviceId) {
          this.loadDevice();
        }
      });
    }
  }

  loadDevice(): void {
    if (!this.deviceId) return;
    
    this.loading = true;
    this.error = null;

    // Load device from client dashboard summary
    this.dashboardService.getClientDashboard().subscribe({
      next: (data) => {
        const foundDevice = data.devices.find(d => d.id === this.deviceId);
        if (foundDevice) {
          this.device = foundDevice;
          this.loading = false;
          this.loadTicketHistory();
        } else {
          this.error = 'Dispositivo no encontrado.';
          this.loading = false;
        }
      },
      error: (err: Error) => {
        console.error('Error loading device:', err);
        this.error = 'No se pudo cargar la información del dispositivo.';
        this.loading = false;
      }
    });
  }

  loadTicketHistory(): void {
    if (!this.deviceId) return;
    
    this.loadingTickets = true;

    // Get all tickets and filter by device
    this.ticketService.listTickets().subscribe({
      next: (tickets: TicketReadMinimal[]) => {
        // Filter tickets for this device
        const deviceTickets = tickets.filter(t => t.device_id === this.deviceId);
        this.tickets = deviceTickets.map((t: TicketReadMinimal) => ({
          id: t.id,
          tracking_code: t.tracking_code,
          failure_desc: t.device_label?.split('–')[1]?.trim() || 'Servicio técnico',
          created_at: t.created_at,
          closed_at: undefined,
          status: {
            name: t.status_name || 'Desconocido',
            code: t.status_code || '',
            color: this.getStatusColor(t.status_code || '')
          }
        }));
        this.loadingTickets = false;
      },
      error: () => {
        this.tickets = [];
        this.loadingTickets = false;
      }
    });
  }

  getStatusColor(code: string): string {
    const colors: Record<string, string> = {
      'RECEIVED': '#3498db',
      'DIAGNOSING': '#9b59b6',
      'WAITING_APPROVAL': '#f39c12',
      'REPAIRING': '#e67e22',
      'WAITING_PARTS': '#95a5a6',
      'READY': '#27ae60',
      'DELIVERED': '#2ecc71',
      'CLOSED': '#7f8c8d',
      'CANCELLED': '#e74c3c'
    };
    return colors[code.toUpperCase()] || '#1a5c3a';
  }

  goBack(): void {
    this.router.navigate(['/client/devices']);
  }

  viewTicket(ticketId: number): void {
    this.router.navigate(['/client/tickets', ticketId]);
  }

  getDeviceIcon(type: string): string {
    const icons: Record<string, string> = {
      'PHONE': '📱',
      'LAPTOP': '💻',
      'TABLET': '📟',
      'OTHER': '🔧'
    };
    return icons[type?.toUpperCase()] || '📦';
  }

  getTypeName(type: string): string {
    const names: Record<string, string> = {
      'PHONE': 'Teléfono',
      'LAPTOP': 'Laptop',
      'TABLET': 'Tablet',
      'OTHER': 'Otro'
    };
    return names[type?.toUpperCase()] || type;
  }

  getCompletedCount(): number {
    const completedStatuses = ['CLOSED', 'DELIVERED'];
    return this.tickets.filter(t => 
      completedStatuses.includes(t.status.code.toUpperCase())
    ).length;
  }

  getActiveCount(): number {
    const completedStatuses = ['CLOSED', 'DELIVERED', 'CANCELLED'];
    return this.tickets.filter(t => 
      !completedStatuses.includes(t.status.code.toUpperCase())
    ).length;
  }
}
