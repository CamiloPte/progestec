// src/app/client-portal/client-ticket-detail/client-ticket-detail.component.ts
import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { TicketService } from '../../core/services/ticket.service';
import { TicketReadDetail } from '../../core/models/ticket';

@Component({
  selector: 'app-client-ticket-detail',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './client-ticket-detail.component.html',
  styleUrls: ['./client-ticket-detail.component.css'],
})
export class ClientTicketDetailComponent implements OnInit {
  ticket: TicketReadDetail | null = null;
  loading = true;
  error: string | null = null;
  isBrowser: boolean;
  
  approvingBudget = false;
  downloadingPdf = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private ticketService: TicketService,
    @Inject(PLATFORM_ID) platformId: object
  ) {
    this.isBrowser = isPlatformBrowser(platformId);
  }

  ngOnInit(): void {
    if (this.isBrowser) {
      const id = Number(this.route.snapshot.paramMap.get('id'));
      if (id) {
        this.loadTicket(id);
      }
    }
  }

  loadTicket(id: number): void {
    this.loading = true;
    this.ticketService.getTicketDetail(id).subscribe({
      next: (data) => {
        this.ticket = data;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error:', err);
        this.error = 'No se pudo cargar el ticket.';
        this.loading = false;
      }
    });
  }

  goBack(): void {
    this.router.navigate(['/client/tickets']);
  }

  approveBudget(): void {
    if (!this.ticket) return;
    
    if (confirm(`¿Confirmas aprobar el presupuesto de $${this.ticket.cost_estimate?.toLocaleString() || 0}?\n\nAl aprobar, se procederá con la reparación de tu equipo.`)) {
      this.approvingBudget = true;
      this.ticketService.respondToQuote(this.ticket.id, true).subscribe({
        next: (updatedTicket) => {
          this.approvingBudget = false;
          this.ticket = updatedTicket;
          alert('¡Presupuesto aprobado! Procederemos con la reparación de tu equipo. Te notificaremos cuando esté listo.');
        },
        error: (err) => {
          console.error('Error:', err);
          this.approvingBudget = false;
          alert(err.error?.detail || 'No se pudo aprobar el presupuesto. Intenta de nuevo.');
        }
      });
    }
  }

  rejectBudget(): void {
    if (!this.ticket) return;
    
    const reason = prompt('¿Por qué rechazas el presupuesto? (opcional)');
    
    if (confirm('¿Estás seguro de rechazar el presupuesto?\n\nTu equipo quedará pendiente de recoger sin cargo.')) {
      this.approvingBudget = true;
      this.ticketService.respondToQuote(this.ticket.id, false, reason || undefined).subscribe({
        next: (updatedTicket) => {
          this.approvingBudget = false;
          this.ticket = updatedTicket;
          alert('Presupuesto rechazado. Tu equipo está listo para recoger en nuestras instalaciones sin ningún cargo.');
        },
        error: (err) => {
          console.error('Error:', err);
          this.approvingBudget = false;
          alert(err.error?.detail || 'No se pudo procesar. Intenta de nuevo.');
        }
      });
    }
  }

  downloadReceptionPdf(): void {
    if (!this.ticket) return;
    this.downloadingPdf = true;
    
    this.ticketService.downloadReceptionPdf(this.ticket.id).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `recepcion_${this.ticket!.tracking_code}.pdf`;
        a.click();
        window.URL.revokeObjectURL(url);
        this.downloadingPdf = false;
      },
      error: (err) => {
        console.error('Error:', err);
        alert('No se pudo descargar el PDF.');
        this.downloadingPdf = false;
      }
    });
  }

  getProgressPercent(): number {
    if (!this.ticket?.status) return 0;
    const progressMap: Record<string, number> = {
      'RECEIVED': 10,
      'DIAGNOSING': 25,
      'WAITING_APPROVAL': 35,
      'APPROVED': 45,
      'IN_PROGRESS': 60,
      'READY': 85,
      'DELIVERED': 95,
      'CLOSED': 100,
      'CANCELLED': 100,
    };
    return progressMap[this.ticket.status.code?.toUpperCase() || ''] || 0;
  }

  getStatusColor(): string {
    if (!this.ticket?.status) return '#7f8c8d';
    const colorMap: Record<string, string> = {
      'RECEIVED': '#3498db',
      'DIAGNOSING': '#9b59b6',
      'WAITING_APPROVAL': '#f39c12',
      'APPROVED': '#27ae60',
      'IN_PROGRESS': '#2980b9',
      'READY': '#2ecc71',
      'DELIVERED': '#1abc9c',
      'CLOSED': '#95a5a6',
      'CANCELLED': '#e74c3c',
    };
    return colorMap[this.ticket.status.code?.toUpperCase() || ''] || '#7f8c8d';
  }

  needsApproval(): boolean {
    // El cliente puede aprobar/rechazar cuando el ticket está en WAITING_APPROVAL
    return this.ticket?.status?.code?.toUpperCase() === 'WAITING_APPROVAL';
  }

  isApproved(): boolean {
    // El ticket fue aprobado si está en REPAIRING, READY, DELIVERED o CLOSED
    const approvedStatuses = ['REPAIRING', 'READY', 'DELIVERED', 'CLOSED'];
    return approvedStatuses.includes(this.ticket?.status?.code?.toUpperCase() || '');
  }

  isCancelled(): boolean {
    return this.ticket?.status?.code?.toUpperCase() === 'CANCELLED';
  }

  isReady(): boolean {
    return this.ticket?.status?.code?.toUpperCase() === 'READY';
  }
}
