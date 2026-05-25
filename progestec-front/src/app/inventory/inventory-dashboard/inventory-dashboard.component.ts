// Componente de dashboard de inventario: muestra KPIs, listado de repuestos y modales de creación/movimientos.
import { Component, Inject, OnInit } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { HttpErrorResponse } from '@angular/common/http';
import { PLATFORM_ID } from '@angular/core';

import { AuthenticatedLayoutComponent } from '../../core/layouts/authenticated-layout.component';
import { InventoryService } from '../../core/services/inventory.service';
import {
  InventorySummary,
  InventoryPart,
  InventoryPartPayload,
  MovementPayload,
} from '../../core/models/inventory';
import { AuthService } from '../../core/services/auth.service';
import { PermissionService } from '../../core/services/permission.service';
import { CurrentUser } from '../../core/models/user';

@Component({
  selector: 'app-inventory-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule, AuthenticatedLayoutComponent],
  templateUrl: './inventory-dashboard.component.html',
  styleUrls: ['./inventory-dashboard.component.css'],
})
export class InventoryDashboardComponent implements OnInit {
  currentUser: CurrentUser | null = null;
  isAdminOrAdvisor = false;
  private isBrowser = false;

  // Opciones fijas para desplegable de categoría
  categoryOptions: string[] = [
    'Pantallas',
    'Baterías',
    'Cámaras',
    'Placas',
    'Componentes internos',
    'Accesorios',
    'Otros',
  ];

  summary: InventorySummary | null = null;
  summaryLoading = false;
  summaryError: string | null = null;

  parts: InventoryPart[] = [];
  partsLoading = false;
  partsError: string | null = null;

  search = '';
  categoryFilter = 'ALL';
  statusFilter = 'ALL';

  // Modal de repuesto
  showPartModal = false;
  partModalMode: 'create' | 'edit' = 'create';
  partSaving = false;
  partError: string | null = null;
  editingPartId: number | null = null;
  partForm: InventoryPartPayload = this.getEmptyPartForm();

  // Modal de movimiento
  showMovementModal = false;
  movementSaving = false;
  movementError: string | null = null;
  movementForm = this.getEmptyMovementForm();

  constructor(
    private inventoryService: InventoryService,
    private router: Router,
    private authService: AuthService,
    private permissionService: PermissionService,
    @Inject(PLATFORM_ID) private platformId: Object,
  ) {}

  ngOnInit(): void {
    this.isBrowser = isPlatformBrowser(this.platformId);
    if (!this.isBrowser) {
      return;
    }

    this.currentUser = this.authService.getCurrentUser();
    this.isAdminOrAdvisor =
      !!this.currentUser &&
      (this.permissionService.isAdmin(this.currentUser) ||
        this.permissionService.isAdvisor(this.currentUser));

    this.loadSummary();
    this.loadParts();
  }

  // ====== Resumen ======
  private loadSummary(): void {
    if (!this.isBrowser) {
      return;
    }
    this.summaryLoading = true;
    this.summaryError = null;

    this.inventoryService.getSummary().subscribe({
      next: (summary) => {
        this.summary = summary;
        this.summaryLoading = false;
      },
      error: () => {
        this.summaryError = 'No se pudo cargar el resumen de inventario.';
        this.summaryLoading = false;
      },
    });
  }

  // ====== Listado de repuestos ======
  loadParts(): void {
    if (!this.isBrowser) {
      return;
    }
    this.partsLoading = true;
    this.partsError = null;

    this.inventoryService
      .getParts({
        search: this.search,
        category: this.categoryFilter,
        status: this.statusFilter,
      })
      .subscribe({
        next: (parts) => {
          this.parts = parts;
          this.partsLoading = false;

          if (!this.parts.length) {
            this.movementForm.part_id = null;
          } else if (!this.movementForm.part_id) {
            this.movementForm.part_id = this.parts[0].id;
          }
        },
        error: () => {
          this.partsError = 'No se pudieron cargar los repuestos.';
          this.partsLoading = false;
        },
      });
  }

  onSearchChange(): void {
    this.loadParts();
  }

  getStatusLabel(part: InventoryPart): string {
    if (part.stock_current <= 0) return 'Crítico';
    if (part.stock_current <= part.stock_min) return 'Bajo';
    return 'En stock';
  }

  getStatusClass(part: InventoryPart): string {
    if (part.stock_current <= 0) return 'pill pill-danger';
    if (part.stock_current <= part.stock_min) return 'pill pill-warning';
    return 'pill pill-success';
  }

  getCategoryPercentage(categoryKey: string): number {
    if (!this.summary || !this.summary.stock_by_category) return 0;

    const total = Object.values(this.summary.stock_by_category).reduce(
      (sum, value) => sum + value,
      0,
    );
    if (!total) return 0;

    const categoryTotal = this.summary.stock_by_category[categoryKey] || 0;
    return (categoryTotal / total) * 100;
  }

  // ====== Movimientos desde dashboard ======
  onCreateMovement(): void {
    if (!this.isBrowser || !this.parts.length) {
      return;
    }
    this.openMovementModal();
  }

  openMovementModal(part?: InventoryPart): void {
    if (!this.isBrowser || !this.parts.length) {
      return;
    }
    this.movementError = null;
    this.movementForm = this.getEmptyMovementForm();
    if (part) {
      this.movementForm.part_id = part.id;
    }
    this.showMovementModal = true;
  }

  closeMovementModal(): void {
    this.showMovementModal = false;
    this.movementError = null;
  }

  submitMovementModal(): void {
    if (!this.isBrowser) {
      return;
    }
    if (!this.movementForm.part_id) {
      this.movementError = 'Selecciona un repuesto.';
      return;
    }
    if (!this.movementForm.quantity || this.movementForm.quantity <= 0) {
      this.movementError = 'La cantidad debe ser mayor a 0.';
      return;
    }

    const payload: MovementPayload = {
      movement_type: this.movementForm.movement_type,
      quantity: this.movementForm.quantity,
      document_ref: this.movementForm.document_ref || undefined,
      movement_at: this.movementForm.movement_at
        ? new Date(this.movementForm.movement_at).toISOString()
        : undefined,
      notes: this.movementForm.notes || undefined,
    };

    this.movementSaving = true;
    this.inventoryService
      .registerMovement(this.movementForm.part_id, payload)
      .subscribe({
        next: () => {
          this.movementSaving = false;
          this.closeMovementModal();
          this.loadSummary();
          this.loadParts();
        },
        error: (err) => {
          if (err instanceof HttpErrorResponse && err.status === 403 && err.error?.detail) {
            this.movementError = err.error.detail;
          } else {
            this.movementError = 'No se pudo registrar el movimiento.';
          }
          this.movementSaving = false;
        },
      });
  }

  // ====== Modal de repuesto (crear/editar) ======
  openPartModal(part?: InventoryPart): void {
    if (!this.isBrowser || !this.isAdminOrAdvisor) {
      return;
    }
    this.partError = null;
    this.partModalMode = part ? 'edit' : 'create';
    this.showPartModal = true;
    this.partSaving = false;

    if (part) {
      this.editingPartId = part.id;
      this.partForm = {
        name: part.name,
        sku: part.sku || '',
        unit_price: part.unit_price,
        category: part.category || '',
        manufacturer: part.manufacturer || '',
        compatible_models: part.compatible_models || '',
        preferred_vendor: part.preferred_vendor || '',
        notes: part.notes || '',
        stock_current: part.stock_current,
        stock_min: part.stock_min,
        requires_approval: part.requires_approval,
      };
    } else {
      this.editingPartId = null;
      this.partForm = this.getEmptyPartForm();
    }
  }

  closePartModal(): void {
    this.showPartModal = false;
    this.partError = null;
  }

  submitPartForm(): void {
    if (!this.isBrowser) {
      return;
    }
    if (!this.partForm.name.trim()) {
      this.partError = 'El nombre es obligatorio.';
      return;
    }
    if (!this.partForm.unit_price || this.partForm.unit_price <= 0) {
      this.partError = 'El costo unitario debe ser mayor a 0.';
      return;
    }

    const payload: InventoryPartPayload = {
      ...this.partForm,
      name: this.partForm.name.trim(),
      sku: this.partForm.sku?.trim() || undefined, // el backend lo genera, pero dejamos el campo para edición/visual
      category: this.partForm.category?.trim() || undefined,
      manufacturer: this.partForm.manufacturer?.trim() || undefined,
      compatible_models: this.partForm.compatible_models?.trim() || undefined,
      preferred_vendor: this.partForm.preferred_vendor?.trim() || undefined,
      notes: this.partForm.notes?.trim() || undefined,
      unit_price: Number(this.partForm.unit_price),
      stock_current: Number(this.partForm.stock_current) || 0,
      stock_min: Number(this.partForm.stock_min) || 0,
      requires_approval: !!this.partForm.requires_approval,
    };

    this.partSaving = true;
    const request$ =
      this.partModalMode === 'create'
        ? this.inventoryService.createPart(payload)
        : this.inventoryService.updatePart(this.editingPartId!, payload);

    request$.subscribe({
      next: () => {
        this.partSaving = false;
        this.closePartModal();
        this.loadSummary();
        this.loadParts();
      },
      error: (err) => {
        if (err instanceof HttpErrorResponse && err.status === 403 && err.error?.detail) {
          this.partError = err.error.detail;
        } else {
          this.partError = 'No se pudo guardar el repuesto.';
        }
        this.partSaving = false;
      },
    });
  }

  deletePart(part: InventoryPart): void {
    if (!this.isBrowser || !this.isAdminOrAdvisor) {
      return;
    }
    const confirmDelete = confirm(`¿Eliminar el repuesto "${part.name}"?`);
    if (!confirmDelete) {
      return;
    }

    this.inventoryService.deletePart(part.id).subscribe({
      next: () => {
        this.loadSummary();
        this.loadParts();
      },
      error: () => {
        alert('No se pudo eliminar el repuesto.');
      },
    });
  }

  // ====== Navegación ======
  viewDetail(part: InventoryPart): void {
    if (!this.isBrowser) {
      return;
    }
    this.router.navigate(['/inventario', part.id]);
  }

  // ====== Helpers de formularios ======
  private getEmptyPartForm(): InventoryPartPayload {
    return {
      name: '',
      sku: '',
      unit_price: 0,
      category: '',
      manufacturer: '',
      compatible_models: '',
      preferred_vendor: '',
      notes: '',
      stock_current: 0,
      stock_min: 0,
      requires_approval: false,
    };
  }

  private getEmptyMovementForm() {
    return {
      part_id: this.parts.length ? this.parts[0].id : null,
      movement_type: 'IN' as 'IN' | 'OUT',
      quantity: 1,
      document_ref: '',
      movement_at: '',
      notes: '',
    };
  }
}
