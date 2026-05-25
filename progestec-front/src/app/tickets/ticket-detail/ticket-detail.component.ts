import { Component, OnDestroy, OnInit, Inject } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { Subscription } from 'rxjs';

import { TicketService } from '../../core/services/ticket.service';
import { UserService } from '../../core/services/user.service';
import { TicketStatusService } from '../../core/services/ticket-status.service';
import { AuthenticatedLayoutComponent } from '../../core/layouts/authenticated-layout.component';
import { AuthService } from '../../core/services/auth.service';

import { TicketReadDetail } from '../../core/models/ticket';
import { UserReadMinimal, CurrentUser } from '../../core/models/user';
import { TicketStatusRead } from '../../core/models/ticket-status';
import { TicketHistoryRead } from '../../core/models/ticket-history';
import { TicketAttachmentRead } from '../../core/models/ticket-attachment';
import { PermissionService } from '../../core/services/permission.service';
import { API_BASE_URL } from '../../core/config/api.config';
import { InvoiceService } from '../../core/services/invoice.service';
import { InventoryService } from '../../core/services/inventory.service';
import { Invoice, InvoiceCreateDto } from '../../core/models/invoice';
import { TicketPartRead, TicketPartCreate } from '../../core/models/ticket-part';
import { InventoryPart } from '../../core/models/inventory';
import { PLATFORM_ID } from '@angular/core';

@Component({
  selector: 'app-ticket-detail',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule, AuthenticatedLayoutComponent],
  templateUrl: './ticket-detail.component.html',
  styleUrls: ['./ticket-detail.component.css'],
})
export class TicketDetailComponent implements OnInit, OnDestroy {
  ticket: TicketReadDetail | null = null;
  technicians: UserReadMinimal[] = [];
  statuses: TicketStatusRead[] = [];
  selectedTechnicianId: number | null = null;
  selectedStatusId: number | null = null;
  ticketParts: TicketPartRead[] = [];
  partsCost = 0;
  availableParts: InventoryPart[] = [];
  downloadingPdf = false;

  loading = false;
  assigning = false;
  error: string | null = null;
  assignFeedback: string | null = null;
  statusLoading = false;
  currentUser: CurrentUser | null = null;
  partsLoading = false;
  invoiceLoading = false;
  invoice: Invoice | null = null;
  invoiceError: string | null = null;
  private subs = new Subscription();
  private currentTicketId: number | null = null;
  deletingAttachmentId: number | null = null;
  deleteModal = {
    open: false,
    file: null as TicketAttachmentRead | null,
    loading: false,
    error: '',
  };

  statusModal = {
    open: false,
    statusId: null as number | null,
    note: '',
    file: null as File | null,
    saving: false,
    error: '',
    loadingTransitions: false,
    validTransitions: [] as TicketStatusRead[],
  };

  diagnosisModal = {
    open: false,
    diagnosis: '',
    note: '',
    file: null as File | null,
    saving: false,
    error: '',
  };

  budgetModal = {
    open: false,
    amount: '',
    note: '',
    file: null as File | null,
    saving: false,
    error: '',
  };

  invoiceModal = {
    open: false,
    saving: false,
    error: '',
    form: {
      labor_cost: 0,
      discount_amount: 0,
      tax_percentage: 19,
      due_date: '',
      notes: '',
    },
    preview: {
      parts: 0,
      labor: 0,
      discount: 0,
      subtotal: 0,
      tax: 0,
      total: 0,
    },
  };

  partsModal = {
    open: false,
    saving: false,
    error: '',
    selectedPartId: null as number | null,
    qty: 1,
    notes: '',
  };

  removingPartId: number | null = null;

  private isBrowser = false;

  constructor(
    private route: ActivatedRoute,
    private ticketService: TicketService,
    private userService: UserService,
    private ticketStatusService: TicketStatusService,
    private authService: AuthService,
    private permissionService: PermissionService,
    private invoiceService: InvoiceService,
    private inventoryService: InventoryService,
    @Inject(PLATFORM_ID) private platformId: Object,
  ) {}

  ngOnInit(): void {
    this.isBrowser = isPlatformBrowser(this.platformId);
    if (!this.isBrowser) {
      return;
    }

    const ticketIdParam = this.route.snapshot.paramMap.get('id');
    const ticketId = ticketIdParam ? Number(ticketIdParam) : NaN;

    if (!ticketIdParam || Number.isNaN(ticketId)) {
      this.error = 'ID de ticket inválido.';
      return;
    }

    this.currentTicketId = ticketId;

    const userSub = this.authService.currentUser$.subscribe((user) => {
      this.currentUser = user;
    });
    this.subs.add(userSub);

    this.loadTicket(ticketId);
    this.loadTechnicians();
    this.loadStatuses();
    this.loadTicketParts(ticketId);
    this.loadInvoice(ticketId);
  }

  ngOnDestroy(): void {
    this.subs.unsubscribe();
  }

  // Obtiene el detalle del ticket desde el backend.
  private loadTicket(ticketId: number): void {
    if (!this.isBrowser) {
      return;
    }
    this.loading = true;
    this.ticketService.getTicketDetail(ticketId).subscribe({
      next: (ticket) => {
        this.applyTicket(ticket);
        this.loading = false;
      },
      error: (err) => {
        console.error('Error cargando ticket', err);
        this.error = 'No se pudo cargar el ticket solicitado.';
        this.loading = false;
      },
    });
  }

  private loadTicketParts(ticketId: number): void {
    if (!this.isBrowser) {
      return;
    }
    this.partsLoading = true;
    this.ticketService.listTicketParts(ticketId).subscribe({
      next: (items) => {
        this.ticketParts = items;
        this.partsCost = items.reduce((acc, item) => acc + Number(item.total_cost || 0), 0);
        this.updateInvoicePreview();
      },
      error: () => {
        this.ticketParts = [];
        this.partsCost = 0;
      },
      complete: () => {
        this.partsLoading = false;
      },
    });
  }

  private loadInvoice(ticketId: number): void {
    if (!this.isBrowser) {
      return;
    }
    this.invoiceLoading = true;
    this.invoiceService.getInvoiceForTicket(ticketId).subscribe({
      next: (invoice) => {
        this.invoice = invoice;
        this.invoiceError = null;
      },
      error: () => {
        this.invoice = null;
        this.invoiceError = 'No se pudo cargar la información de facturación.';
      },
      complete: () => {
        this.invoiceLoading = false;
      },
    });
  }

  // Carga técnicos disponibles para el combo de asignación.
  private loadTechnicians(): void {
    if (!this.isBrowser) {
      return;
    }
    this.userService.listTechnicians().subscribe({
      next: (list) => {
        this.technicians = list;
      },
      error: () => {
        console.warn('No se pudo cargar la lista de técnicos.');
      },
    });
  }

  // Carga los estados activos para desplegarlos en selectores y modales.
  private loadStatuses(): void {
    if (!this.isBrowser) {
      return;
    }
    this.statusLoading = true;
    this.ticketStatusService.listStatuses().subscribe({
      next: (items) => {
        this.statuses = items;
        if (this.ticket) {
          this.selectedStatusId = this.ticket.status?.id ?? null;
        }
      },
      error: () => {
        console.warn('No se pudieron cargar los estados.');
      },
      complete: () => {
        this.statusLoading = false;
      },
    });
  }

  // Sincroniza el estado local del componente con la respuesta del backend.
  private applyTicket(updated: TicketReadDetail): void {
    this.ticket = updated;
    this.selectedTechnicianId = updated.assignee_user_id ?? null;
    this.selectedStatusId = updated.status?.id ?? null;
  }

  // Refresca el detalle con el ID actual.
  private reloadTicket(): void {
    if (this.currentTicketId !== null) {
      this.loadTicket(this.currentTicketId);
      this.loadInvoice(this.currentTicketId);
      this.loadTicketParts(this.currentTicketId);
    }
  }

  // Construye la clase visual del estado principal.
  getStatusChipClass(): string {
    const code = (this.ticket?.status.code || '').toUpperCase();
    if (code === 'CLOSED') {
      return 'status-chip status-chip--success';
    }
    if (code === 'DELIVERED') {
      return 'status-chip status-chip--success';
    }
    if (code === 'READY') {
      return 'status-chip status-chip--success';
    }
    if (code === 'DIAGNOSING') {
      return 'status-chip status-chip--diagnosis';
    }
    if (code === 'WAITING_APPROVAL') {
      return 'status-chip status-chip--approval';
    }
    if (code === 'REPAIRING' || code === 'IN_PROGRESS') {
      return 'status-chip status-chip--warning';
    }
    if (code === 'RECEIVED' || code === 'OPEN') {
      return 'status-chip status-chip--info';
    }
    if (code === 'CANCELLED') {
      return 'status-chip status-chip--cancelled';
    }
    return 'status-chip status-chip--neutral';
  }

  // Determina la clase para cada evento del timeline.
  getTimelineBadgeClass(entry: TicketHistoryRead): string {
    const code = (entry.status_code || '').toUpperCase();
    if (code === 'CLOSED') {
      return 'timeline-badge timeline-badge--success';
    }
    if (code === 'DELIVERED') {
      return 'timeline-badge timeline-badge--delivered';
    }
    if (code === 'READY') {
      return 'timeline-badge timeline-badge--ready';
    }
    if (code === 'DIAGNOSING') {
      return 'timeline-badge timeline-badge--diagnosis';
    }
    if (code === 'WAITING_APPROVAL') {
      return 'timeline-badge timeline-badge--approval';
    }
    if (code === 'REPAIRING' || code === 'IN_PROGRESS') {
      return 'timeline-badge timeline-badge--warning';
    }
    if (code === 'RECEIVED' || code === 'OPEN') {
      return 'timeline-badge timeline-badge--info';
    }
    if (code === 'CANCELLED') {
      return 'timeline-badge timeline-badge--cancelled';
    }
    return 'timeline-badge';
  }

  // Determina el icono para cada evento del timeline
  getTimelineIconClass(entry: TicketHistoryRead): string {
    const code = (entry.status_code || '').toUpperCase();
    if (code === 'CLOSED' || code === 'DELIVERED' || code === 'READY') {
      return 'timeline-icon timeline-icon--success';
    }
    if (code === 'DIAGNOSING') {
      return 'timeline-icon timeline-icon--diagnosis';
    }
    if (code === 'WAITING_APPROVAL') {
      return 'timeline-icon timeline-icon--approval';
    }
    if (code === 'REPAIRING' || code === 'IN_PROGRESS') {
      return 'timeline-icon timeline-icon--warning';
    }
    if (code === 'CANCELLED') {
      return 'timeline-icon timeline-icon--cancelled';
    }
    if (code === 'RECEIVED' || code === 'OPEN') {
      return 'timeline-icon timeline-icon--info';
    }
    return 'timeline-icon timeline-icon--default';
  }

  // Detecta si la nota es automática (generada por el sistema)
  isAutoNote(note: string): boolean {
    if (!note) return true;
    const autoPatterns = [
      /^Status changed to/i,
      /^Estado actualizado a/i,
      /^Ticket created/i,
      /^Ticket creado/i,
    ];
    return autoPatterns.some(pattern => pattern.test(note.trim()));
  }

  // Obtiene el título del timeline según el tipo de evento
  getTimelineTitle(entry: TicketHistoryRead): string {
    const code = (entry.status_code || '').toUpperCase();
    if (code === 'DIAGNOSING' && entry.note?.toLowerCase().includes('diagnóstico')) {
      return 'Diagnóstico actualizado';
    }
    if (code === 'RECEIVED' || code === 'OPEN') {
      return 'Ticket Creado';
    }
    return entry.status_name || entry.status_code || 'Actualización';
  }

  // Clase para el estado en el timeline
  getTimelineStatusClass(entry: TicketHistoryRead): string {
    const code = (entry.status_code || '').toUpperCase();
    if (code === 'CLOSED' || code === 'DELIVERED' || code === 'READY') {
      return 'status-text status-text--success';
    }
    if (code === 'DIAGNOSING') {
      return 'status-text status-text--diagnosis';
    }
    if (code === 'WAITING_APPROVAL') {
      return 'status-text status-text--approval';
    }
    if (code === 'REPAIRING' || code === 'IN_PROGRESS') {
      return 'status-text status-text--warning';
    }
    if (code === 'RECEIVED' || code === 'OPEN') {
      return 'status-text status-text--info';
    }
    return 'status-text';
  }

  get timelineItems(): TicketHistoryRead[] {
    return this.ticket?.history || [];
  }

  get intakeImages(): TicketAttachmentRead[] {
    if (!this.ticket?.attachments) {
      return [];
    }
    return this.ticket.attachments.filter(
      (file) =>
        (file.attachment_type || '').toLowerCase() === 'intake' &&
        this.isImageAttachment(file)
    );
  }

  get otherAttachments(): TicketAttachmentRead[] {
    if (!this.ticket?.attachments) {
      return [];
    }
    return this.ticket.attachments.filter(
      (file) => (file.attachment_type || '').toLowerCase() !== 'intake'
    );
  }

  get canGenerateInvoice(): boolean {
    return (
      this.permissionService.isAdmin(this.currentUser) ||
      this.permissionService.isAdvisor(this.currentUser)
    );
  }

  get invoiceStatusClass(): string {
    const status = (this.invoice?.status || '').toUpperCase();
    if (status === 'PAID') {
      return 'invoice-chip invoice-chip--success';
    }
    if (status === 'CANCELLED') {
      return 'invoice-chip invoice-chip--danger';
    }
    return 'invoice-chip invoice-chip--pending';
  }

  get outstandingAmount(): number {
    return this.invoice?.outstanding_amount ?? 0;
  }

  get invoiceDetailLink(): (string | number)[] {
    if (!this.invoice) {
      return [];
    }
    if (this.permissionService.isClient(this.currentUser)) {
      return ['/mis-facturas', this.invoice.id];
    }
    return ['/facturacion', this.invoice.id];
  }

  openInvoiceModal(): void {
    if (!this.ticket) {
      return;
    }
    this.invoiceModal.form = {
      labor_cost: 0,
      discount_amount: 0,
      tax_percentage: 19,
      due_date: this.formatLocalDateString(new Date()),
      notes: '',
    };
    this.invoiceModal.error = '';
    this.invoiceModal.saving = false;
    this.updateInvoicePreview();
    this.invoiceModal.open = true;
  }

  closeInvoiceModal(): void {
    this.invoiceModal.open = false;
    this.invoiceModal.saving = false;
    this.invoiceModal.error = '';
  }

  onInvoiceFieldChange(): void {
    this.updateInvoicePreview();
  }

  submitInvoiceModal(): void {
    if (!this.ticket || this.invoiceModal.saving) {
      return;
    }
    const payload: InvoiceCreateDto = {
      labor_cost: this.toNumber(this.invoiceModal.form.labor_cost),
      discount_amount: this.toNumber(this.invoiceModal.form.discount_amount),
      tax_percentage: this.toNumber(this.invoiceModal.form.tax_percentage),
      due_date: this.invoiceModal.form.due_date || undefined,
      notes: this.invoiceModal.form.notes || undefined,
    };
    this.invoiceModal.saving = true;
    this.invoiceModal.error = '';
    this.invoiceService.createInvoiceFromTicket(this.ticket.id, payload).subscribe({
      next: (invoice) => {
        this.invoice = invoice;
        this.closeInvoiceModal();
        this.loadInvoice(this.ticket!.id);
      },
      error: (err) => {
        console.error('No se pudo generar la factura', err);
        this.invoiceModal.error = err?.error?.detail || 'No se pudo generar la factura.';
        this.invoiceModal.saving = false;
      },
    });
  }

  private updateInvoicePreview(): void {
    const labor = this.toNumber(this.invoiceModal.form.labor_cost);
    const discount = Math.max(0, this.toNumber(this.invoiceModal.form.discount_amount));
    const taxPercentage = this.toNumber(this.invoiceModal.form.tax_percentage);
    const parts = this.partsCost;

    const subtotalBeforeDiscount = parts + labor;
    const appliedDiscount = Math.min(subtotalBeforeDiscount, discount);
    const subtotal = Math.max(0, subtotalBeforeDiscount - appliedDiscount);
    const tax = subtotal * (taxPercentage / 100);
    const total = subtotal + tax;

    this.invoiceModal.preview = {
      parts,
      labor,
      discount: appliedDiscount,
      subtotal,
      tax,
      total,
    };
  }

  private toNumber(value: any): number {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : 0;
  }

  private formatLocalDateString(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  // -------- Gestión de Repuestos --------
  get canManageParts(): boolean {
    const user = this.currentUser;
    return (
      this.permissionService.isAdmin(user) ||
      this.permissionService.isAdvisor(user) ||
      (this.permissionService.isTechnician(user) && this.ticket?.assignee_user_id === user?.id)
    );
  }

  openPartsModal(): void {
    if (!this.ticket || !this.canManageParts) {
      return;
    }
    this.partsModal = {
      open: true,
      saving: false,
      error: '',
      selectedPartId: null,
      qty: 1,
      notes: '',
    };
    this.loadAvailableParts();
  }

  closePartsModal(): void {
    this.partsModal.open = false;
    this.partsModal.error = '';
  }

  private loadAvailableParts(): void {
    this.inventoryService.getParts({ status: 'IN_STOCK' }).subscribe({
      next: (parts) => {
        this.availableParts = parts.filter((p) => p.stock_current > 0);
      },
      error: () => {
        this.availableParts = [];
      },
    });
  }

  getSelectedPartStock(): number {
    if (!this.partsModal.selectedPartId) {
      return 0;
    }
    const part = this.availableParts.find((p) => p.id === this.partsModal.selectedPartId);
    return part?.stock_current ?? 0;
  }

  getSelectedPartPrice(): number {
    if (!this.partsModal.selectedPartId) {
      return 0;
    }
    const part = this.availableParts.find((p) => p.id === this.partsModal.selectedPartId);
    return part?.unit_price ?? 0;
  }

  submitPartsModal(): void {
    if (!this.ticket || this.partsModal.saving) {
      return;
    }
    if (!this.partsModal.selectedPartId) {
      this.partsModal.error = 'Selecciona un repuesto.';
      return;
    }
    if (this.partsModal.qty < 1) {
      this.partsModal.error = 'La cantidad debe ser al menos 1.';
      return;
    }
    if (this.partsModal.qty > this.getSelectedPartStock()) {
      this.partsModal.error = 'No hay suficiente stock disponible.';
      return;
    }

    const payload: TicketPartCreate = {
      part_id: this.partsModal.selectedPartId,
      qty: this.partsModal.qty,
      notes: this.partsModal.notes || undefined,
    };

    this.partsModal.saving = true;
    this.partsModal.error = '';

    this.ticketService.addTicketPart(this.ticket.id, payload).subscribe({
      next: () => {
        this.closePartsModal();
        this.loadTicketParts(this.ticket!.id);
      },
      error: (err) => {
        console.error('No se pudo agregar el repuesto', err);
        this.partsModal.error = err?.error?.detail || 'No se pudo agregar el repuesto.';
        this.partsModal.saving = false;
      },
    });
  }

  removeTicketPart(ticketPartId: number): void {
    if (!this.ticket || this.removingPartId) {
      return;
    }
    this.removingPartId = ticketPartId;
    this.ticketService.removeTicketPart(this.ticket.id, ticketPartId).subscribe({
      next: () => {
        this.removingPartId = null;
        this.loadTicketParts(this.ticket!.id);
      },
      error: (err) => {
        console.error('No se pudo eliminar el repuesto', err);
        this.removingPartId = null;
      },
    });
  }

  get canManageAssignment(): boolean {
    const user = this.currentUser;
    return this.permissionService.isAdmin(user) || this.permissionService.isAdvisor(user);
  }

  get canUpdateStatus(): boolean {
    if (!this.ticket) {
      return false;
    }
    const currentUser = this.currentUser;
    if (this.permissionService.isAdmin(currentUser) || this.permissionService.isAdvisor(currentUser)) {
      return true;
    }
    if (this.permissionService.isTechnician(currentUser)) {
      return this.ticket.assignee_user_id === currentUser?.id;
    }
    return false;
  }

  get canUpdateService(): boolean {
    if (!this.ticket) {
      return false;
    }
    const currentUser = this.currentUser;
    if (this.permissionService.isAdmin(currentUser) || this.permissionService.isAdvisor(currentUser)) {
      return true;
    }
    if (this.permissionService.isTechnician(currentUser)) {
      return this.ticket.assignee_user_id === currentUser?.id;
    }
    return false;
  }

  get canAssignSelf(): boolean {
    const currentUser = this.currentUser;
    return (
      this.permissionService.isTechnician(currentUser) &&
      this.ticket?.assignee_user_id == null
    );
  }

  // Técnico puede quitarse la asignación solo si está en RECEIVED o DIAGNOSING
  get canUnassignSelf(): boolean {
    const currentUser = this.currentUser;
    if (!this.permissionService.isTechnician(currentUser)) {
      return false;
    }
    if (this.ticket?.assignee_user_id !== currentUser?.id) {
      return false;
    }
    const statusCode = (this.ticket?.status?.code || '').toUpperCase();
    return statusCode === 'RECEIVED' || statusCode === 'DIAGNOSING';
  }

  // Solo Admin y Asesor pueden ver el combo de técnicos
  get canSelectTechnician(): boolean {
    const user = this.currentUser;
    return this.permissionService.isAdmin(user) || this.permissionService.isAdvisor(user);
  }

  get canManageAttachments(): boolean {
    const user = this.currentUser;
    if (this.permissionService.isAdmin(user) || this.permissionService.isAdvisor(user)) {
      return true;
    }
    if (this.permissionService.isTechnician(user)) {
      return this.ticket?.assignee_user_id === user?.id;
    }
    return false;
  }

  // Reasigna el ticket con el valor actual del combo.
  onAssign(): void {
    if (!this.ticket) {
      return;
    }

    this.assigning = true;
    this.assignFeedback = null;

    this.ticketService
      .assignTicket(this.ticket.id, this.selectedTechnicianId)
      .subscribe({
        next: (updated) => {
          this.applyTicket(updated);
          this.assigning = false;
          this.assignFeedback = 'Asignación actualizada correctamente.';
        },
        error: (err) => {
          console.error('Error al asignar técnico', err);
          this.assigning = false;
          this.assignFeedback = err?.error?.detail || 'No se pudo asignar el técnico.';
        },
      });
  }

  // Acción rápida para quitar la asignación actual.
  removeAssignment(): void {
    // Admin/Asesor puede quitar cualquier asignación
    // Técnico solo puede quitarse a sí mismo si canUnassignSelf
    if (!this.ticket) {
      return;
    }
    if (!this.canManageAssignment && !this.canUnassignSelf) {
      return;
    }
    this.selectedTechnicianId = null;
    this.onAssign();
  }

  // Acción rápida para auto-asignarse el ticket.
  assignToMe(): void {
    if (!this.ticket || !this.currentUser) {
      return;
    }
    this.selectedTechnicianId = this.currentUser.id;
    this.onAssign();
  }

  // Abre el modal de cambio de estado.
  openStatusModal(): void {
    if (!this.ticket || !this.canUpdateStatus) {
      return;
    }
    this.statusModal = {
      open: true,
      statusId: null, // No preseleccionar - usuario debe elegir
      note: '',
      file: null,
      saving: false,
      error: '',
      loadingTransitions: true,
      validTransitions: [],
    };
    
    // Cargar las transiciones válidas desde el estado actual
    const currentCode = this.ticket.status?.code || 'RECEIVED';
    this.ticketStatusService.getValidTransitions(currentCode).subscribe({
      next: (transitions) => {
        this.statusModal.validTransitions = transitions;
        this.statusModal.loadingTransitions = false;
        if (transitions.length === 0) {
          this.statusModal.error = 'No hay transiciones disponibles desde este estado.';
        }
      },
      error: () => {
        this.statusModal.loadingTransitions = false;
        this.statusModal.error = 'No se pudieron cargar los estados disponibles.';
      },
    });
  }

  // Cierra el modal de cambio de estado.
  closeStatusModal(): void {
    this.statusModal.open = false;
    this.statusModal.note = '';
    this.statusModal.file = null;
    this.statusModal.error = '';
    this.statusModal.validTransitions = [];
    this.statusModal.loadingTransitions = false;
  }

  // Envía el formulario de cambio de estado.
  submitStatusModal(): void {
    if (!this.ticket || !this.statusModal.statusId) {
      this.statusModal.error = 'Selecciona un estado válido.';
      return;
    }
    const selected = this.statusModal.validTransitions.find((st) => st.id === this.statusModal.statusId);
    const note =
      this.statusModal.note.trim() ||
      (selected ? `Estado actualizado a ${selected.name}` : 'Estado actualizado');
    this.statusModal.saving = true;
    this.ticketService
      .updateTicket(this.ticket.id, {
        status_id: this.statusModal.statusId,
        history_note: note,
      })
      .subscribe({
        next: () => {
          this.uploadAttachmentAfterAction(
            this.statusModal.file,
            'status',
            this.statusModal.note,
            () => {
              this.statusModal.saving = false;
              this.closeStatusModal();
              this.reloadTicket();
            },
            () => {
              this.statusModal.saving = false;
              this.statusModal.error = 'No se pudo subir el archivo.';
            }
          );
        },
        error: () => {
          this.statusModal.saving = false;
          this.statusModal.error = 'No se pudo actualizar el estado.';
        },
      });
  }

  // Abre el modal para actualizar diagnóstico.
  openDiagnosisModal(): void {
    if (!this.ticket || !this.canUpdateService) {
      return;
    }
    this.diagnosisModal = {
      open: true,
      diagnosis: this.ticket.diagnosis || '',
      note: '',
      file: null,
      saving: false,
      error: '',
    };
  }

  // Cierra el modal de diagnóstico.
  closeDiagnosisModal(): void {
    this.diagnosisModal.open = false;
    this.diagnosisModal.note = '';
    this.diagnosisModal.file = null;
    this.diagnosisModal.error = '';
  }

  // Envía la actualización de diagnóstico.
  submitDiagnosisModal(): void {
    if (!this.ticket) {
      return;
    }
    if (!this.diagnosisModal.diagnosis.trim()) {
      this.diagnosisModal.error = 'El diagnóstico no puede estar vacío.';
      return;
    }
    const note =
      this.diagnosisModal.note.trim() || 'Diagnóstico actualizado por el técnico.';
    this.diagnosisModal.saving = true;
    this.ticketService
      .updateTicket(this.ticket.id, {
        diagnosis: this.diagnosisModal.diagnosis.trim(),
        history_note: note,
      })
      .subscribe({
        next: () => {
          this.uploadAttachmentAfterAction(
            this.diagnosisModal.file,
            'diagnosis',
            this.diagnosisModal.note,
            () => {
              this.diagnosisModal.saving = false;
              this.closeDiagnosisModal();
              this.reloadTicket();
            },
            () => {
              this.diagnosisModal.saving = false;
              this.diagnosisModal.error = 'No se pudo subir el archivo.';
            }
          );
        },
        error: () => {
          this.diagnosisModal.saving = false;
          this.diagnosisModal.error = 'No se pudo guardar el diagnóstico.';
        },
      });
  }

  // Abre el modal para actualizar presupuesto.
  openBudgetModal(): void {
    if (!this.ticket || !this.canUpdateService) {
      return;
    }
    this.budgetModal = {
      open: true,
      amount: this.ticket.cost_estimate || '',
      note: '',
      file: null,
      saving: false,
      error: '',
    };
  }

  // Cierra el modal de presupuesto.
  closeBudgetModal(): void {
    this.budgetModal.open = false;
    this.budgetModal.note = '';
    this.budgetModal.file = null;
    this.budgetModal.error = '';
  }

  // Envía la actualización de presupuesto.
  submitBudgetModal(): void {
    if (!this.ticket) {
      return;
    }
    if (!this.budgetModal.amount || isNaN(Number(this.budgetModal.amount))) {
      this.budgetModal.error = 'Ingresa un monto válido.';
      return;
    }
    const note =
      this.budgetModal.note.trim() || 'Presupuesto actualizado para el ticket.';
    this.budgetModal.saving = true;
    this.ticketService
      .updateTicket(this.ticket.id, {
        cost_estimate: this.budgetModal.amount,
        history_note: note,
      })
      .subscribe({
        next: () => {
          this.uploadAttachmentAfterAction(
            this.budgetModal.file,
            'budget',
            this.budgetModal.note,
            () => {
              this.budgetModal.saving = false;
              this.closeBudgetModal();
              this.reloadTicket();
            },
            () => {
              this.budgetModal.saving = false;
              this.budgetModal.error = 'No se pudo subir el archivo.';
            }
          );
        },
        error: () => {
          this.budgetModal.saving = false;
          this.budgetModal.error = 'No se pudo guardar el presupuesto.';
        },
      });
  }

  // Permite almacenar el archivo adjunto seleccionado (pendiente de backend).
  handleFileSelection(modal: 'status' | 'diagnosis' | 'budget', event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0] || null;
    if (modal === 'status') {
      this.statusModal.file = file;
    } else if (modal === 'diagnosis') {
      this.diagnosisModal.file = file;
    } else {
      this.budgetModal.file = file;
    }
  }

  // Ejecuta la subida de un adjunto después de una acción principal.
  private uploadAttachmentAfterAction(
    file: File | null,
    type: string,
    note: string | undefined,
    onSuccess: () => void,
    onError: () => void
  ): void {
    if (!file || !this.ticket) {
      onSuccess();
      return;
    }
    const formData = new FormData();
    formData.append('attachment_type', type);
    if (note?.trim()) {
      formData.append('note', note.trim());
    }
    formData.append('file', file);

    this.ticketService.uploadAttachment(this.ticket.id, formData).subscribe({
      next: () => onSuccess(),
      error: () => onError(),
    });
  }

  isImageAttachment(file: TicketAttachmentRead): boolean {
    const mime = (file.mime_type || '').toLowerCase();
    return mime.startsWith('image/');
  }

  resolveFileUrl(file: TicketAttachmentRead): string {
    const url = file.file_url || '';
    if (!url) {
      return '';
    }
    if (url.startsWith('http://') || url.startsWith('https://')) {
      return url;
    }
    const normalized = url.startsWith('/') ? url : `/${url}`;
    return `${API_BASE_URL}${normalized}`;
  }

  openDeleteModal(file: TicketAttachmentRead): void {
    if (!this.canManageAttachments) {
      return;
    }
    this.deleteModal = { open: true, file, loading: false, error: '' };
  }

  closeDeleteModal(): void {
    this.deleteModal = { open: false, file: null, loading: false, error: '' };
  }

  confirmDelete(): void {
    if (!this.ticket || !this.deleteModal.file) {
      return;
    }
    this.deleteModal.loading = true;
    this.deleteModal.error = '';
    const attachmentId = this.deleteModal.file.id;
    this.ticketService.deleteAttachment(this.ticket.id, attachmentId).subscribe({
      next: () => {
        this.deleteModal.loading = false;
        this.closeDeleteModal();
        this.reloadTicket();
      },
      error: (err) => {
        console.error('No se pudo eliminar el adjunto', err);
        this.deleteModal.loading = false;
        this.deleteModal.error = 'No se pudo eliminar el adjunto. Intenta nuevamente.';
      },
    });
  }

  // ========== PDF Downloads ==========
  
  downloadReceptionPdf(): void {
    if (!this.ticket || this.downloadingPdf) return;
    
    this.downloadingPdf = true;
    this.ticketService.downloadReceptionPdf(this.ticket.id).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `recepcion_${this.ticket?.tracking_code || this.ticket?.id}.pdf`;
        link.click();
        window.URL.revokeObjectURL(url);
        this.downloadingPdf = false;
      },
      error: () => {
        alert('No se pudo descargar el comprobante de recepción.');
        this.downloadingPdf = false;
      },
    });
  }

  downloadDeliveryPdf(): void {
    if (!this.ticket || this.downloadingPdf) return;
    
    this.downloadingPdf = true;
    this.ticketService.downloadDeliveryPdf(this.ticket.id).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `entrega_${this.ticket?.tracking_code || this.ticket?.id}.pdf`;
        link.click();
        window.URL.revokeObjectURL(url);
        this.downloadingPdf = false;
      },
      error: () => {
        alert('No se pudo descargar la orden de entrega.');
        this.downloadingPdf = false;
      },
    });
  }
}
