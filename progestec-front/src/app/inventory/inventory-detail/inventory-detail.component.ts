// Componente de detalle de inventario: muestra un repuesto y permite registrar movimientos.
import { Component, OnDestroy, OnInit, Inject, inject } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Subscription } from 'rxjs';

import { AuthenticatedLayoutComponent } from '../../core/layouts/authenticated-layout.component';
import { InventoryService } from '../../core/services/inventory.service';
import {
  InventoryPartDetail,
  InventoryPartMovement,
  MovementPayload,
} from '../../core/models/inventory';
import { PLATFORM_ID } from '@angular/core';

@Component({
  selector: 'app-inventory-detail',
  standalone: true,
  imports: [CommonModule, RouterModule, ReactiveFormsModule, AuthenticatedLayoutComponent],
  templateUrl: './inventory-detail.component.html',
  styleUrls: ['./inventory-detail.component.css'],
})
export class InventoryDetailComponent implements OnInit, OnDestroy {
  movementError: string | null = null;

  part: InventoryPartDetail | null = null;
  loading = false;
  error: string | null = null;

  showMovementModal = false;
  savingMovement = false;
  private isBrowser = false;

  private fb = inject(FormBuilder);

  movementForm = this.fb.group({
    movement_type: ['IN', Validators.required],
    quantity: [1, [Validators.required, Validators.min(1)]],
    document_ref: [''],
    movement_at: [''],
    notes: [''],
  });

  private subs = new Subscription();

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private inventoryService: InventoryService,
    @Inject(PLATFORM_ID) private platformId: Object,
  ) {}

  ngOnInit(): void {
    this.isBrowser = isPlatformBrowser(this.platformId);
    if (!this.isBrowser) {
      return;
    }

    this.subs.add(
      this.route.paramMap.subscribe((params) => {
        const id = Number(params.get('id'));
        if (id) {
          this.loadPart(id);
        } else {
          this.error = 'Identificador de repuesto inválido.';
        }
      }),
    );
  }

  ngOnDestroy(): void {
    this.subs.unsubscribe();
  }

  private loadPart(id: number): void {
    this.loading = true;
    this.error = null;
    this.inventoryService.getPartDetail(id).subscribe({
      next: (part) => {
        this.part = part;
        this.loading = false;
        this.loadMovements(part.id);
      },
      error: () => {
        this.error = 'No se pudo cargar la información del repuesto.';
        this.loading = false;
      },
    });
  }

  get statusLabel(): string {
    if (!this.part) {
      return 'Sin datos';
    }
    if (this.part.stock_current <= 0) {
      return 'Crítico';
    }
    if (this.part.stock_current <= this.part.stock_min) {
      return 'Bajo';
    }
    return 'En stock';
  }

  get statusClass(): string {
    if (!this.part) {
      return 'status-neutral';
    }
    if (this.part.stock_current <= 0) {
      return 'status-danger';
    }
    if (this.part.stock_current <= this.part.stock_min) {
      return 'status-warning';
    }
    return 'status-success';
  }

  openMovementModal(): void {
    this.movementError = null;
    this.showMovementModal = true;
    this.movementForm.reset({
      movement_type: 'IN',
      quantity: 1,
      document_ref: '',
      movement_at: '',
      notes: '',
    });
  }

  closeMovementModal(): void {
    this.showMovementModal = false;
    this.movementError = null;
  }

  submitMovement(): void {
    if (!this.isBrowser) {
      return;
    }
    if (!this.part || this.movementForm.invalid) {
      this.movementForm.markAllAsTouched();
      return;
    }
    this.savingMovement = true;
    const formValue = this.movementForm.value;
    const payload: MovementPayload = {
      movement_type: (formValue.movement_type || 'IN') as 'IN' | 'OUT',
      quantity: formValue.quantity ?? 0,
      document_ref: formValue.document_ref || undefined,
      movement_at: formValue.movement_at
        ? new Date(formValue.movement_at).toISOString()
        : undefined,
      notes: formValue.notes || undefined,
    };
    this.inventoryService
      .registerMovement(this.part.id, payload)
      .subscribe({
        next: (updated) => {
          if (this.part) {
            this.part.stock_current = updated.stock_current;
            this.part.stock_min = updated.stock_min;
            this.part.last_movement_at = updated.last_movement_at;
          }
          this.loadMovements(this.part?.id);
          this.savingMovement = false;
          this.closeMovementModal();
        },
        error: (err) => {
          this.savingMovement = false;
          if (err instanceof HttpErrorResponse && err.status === 403 && err.error?.detail) {
            this.movementError = err.error.detail;
          } else {
            this.movementError = 'No se pudo registrar el movimiento.';
          }
        },
      });
  }

  private loadMovements(partId?: number | null): void {
    if (!this.isBrowser || !partId) {
      return;
    }
    this.inventoryService.getMovements(partId).subscribe({
      next: (movements: InventoryPartMovement[]) => {
        if (this.part) {
          this.part.movements = movements;
        }
      },
    });
  }

  viewAllMovements(): void {
    if (this.part) {
      this.loadMovements(this.part.id);
    }
  }

  backToList(): void {
    this.router.navigate(['/inventario']);
  }
}
