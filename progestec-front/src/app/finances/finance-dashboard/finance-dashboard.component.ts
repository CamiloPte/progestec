import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { Subscription } from 'rxjs';

import { AuthenticatedLayoutComponent } from '../../core/layouts/authenticated-layout.component';
import { FinanceService } from '../../core/services/finance.service';
import {
  FinanceSummary,
  Expense,
  ExpenseCategory,
  ExpenseCreateDto,
} from '../../core/models/finance';
import { InventoryService } from '../../core/services/inventory.service';

@Component({
  selector: 'app-finance-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule, AuthenticatedLayoutComponent],
  templateUrl: './finance-dashboard.component.html',
  styleUrls: ['./finance-dashboard.component.css'],
})
export class FinanceDashboardComponent implements OnInit, OnDestroy {
  summary: FinanceSummary | null = null;
  expenses: Expense[] = [];
  categories: ExpenseCategory[] = [];
  parts: any[] = [];

  loading = true;
  loadingExpenses = false;
  error: string | null = null;

  // Filtros de período
  filters = {
    from_date: '',
    to_date: '',
    months_back: 6,
  };

  // Modal de gastos
  expenseModal = false;
  submittingExpense = false;
  expenseError: string | null = null;
  expenseForm: ExpenseCreateDto = {
    category_id: 0,
    description: '',
    amount: 0,
    payment_method: 'CASH',
    reference: '',
    expense_date: '',
    part_id: undefined,
    quantity: undefined,
    supplier_name: '',
    notes: '',
  };

  private subs = new Subscription();

  constructor(
    private financeService: FinanceService,
    private inventoryService: InventoryService,
  ) {}

  ngOnInit(): void {
    // Configurar fechas por defecto (último mes)
    const today = new Date();
    const monthAgo = new Date();
    monthAgo.setMonth(monthAgo.getMonth() - 1);

    this.filters.to_date = today.toISOString().split('T')[0];
    this.filters.from_date = monthAgo.toISOString().split('T')[0];

    this.loadSummary();
    this.loadExpenses();
    this.loadCategories();
  }

  ngOnDestroy(): void {
    this.subs.unsubscribe();
  }

  loadSummary(): void {
    this.loading = true;
    this.error = null;

    const sub = this.financeService
      .getSummary({
        from_date: this.filters.from_date || undefined,
        to_date: this.filters.to_date || undefined,
        include_trends: true,
        months_back: this.filters.months_back,
      })
      .subscribe({
        next: (data) => {
          this.summary = data;
          this.loading = false;
        },
        error: (err) => {
          console.error('Error cargando resumen financiero', err);
          this.error = 'No se pudo cargar el resumen financiero.';
          this.loading = false;
        },
      });
    this.subs.add(sub);
  }

  loadExpenses(): void {
    this.loadingExpenses = true;

    const sub = this.financeService
      .listExpenses({
        from_date: this.filters.from_date || undefined,
        to_date: this.filters.to_date || undefined,
      })
      .subscribe({
        next: (data) => {
          this.expenses = data;
          this.loadingExpenses = false;
        },
        error: (err) => {
          console.error('Error cargando gastos', err);
          this.loadingExpenses = false;
        },
      });
    this.subs.add(sub);
  }

  loadCategories(): void {
    const sub = this.financeService.listCategories().subscribe({
      next: (data) => {
        this.categories = data;
      },
      error: (err) => console.error('Error cargando categorías', err),
    });
    this.subs.add(sub);
  }

  loadParts(): void {
    const sub = this.inventoryService.getParts().subscribe({
      next: (data) => {
        this.parts = data;
      },
      error: (err) => console.error('Error cargando repuestos', err),
    });
    this.subs.add(sub);
  }

  applyFilters(): void {
    this.loadSummary();
    this.loadExpenses();
  }

  // ========== Modal de Gastos ==========
  openExpenseModal(): void {
    this.expenseForm = {
      category_id: this.categories.length > 0 ? this.categories[0].id : 0,
      description: '',
      amount: 0,
      payment_method: 'CASH',
      reference: '',
      expense_date: new Date().toISOString().split('T')[0],
      part_id: undefined,
      quantity: undefined,
      supplier_name: '',
      notes: '',
    };
    this.expenseError = null;
    this.loadParts();
    this.expenseModal = true;
  }

  closeExpenseModal(): void {
    this.expenseModal = false;
  }

  submitExpense(): void {
    if (!this.expenseForm.category_id || !this.expenseForm.description || !this.expenseForm.amount) {
      this.expenseError = 'Complete los campos obligatorios';
      return;
    }

    this.submittingExpense = true;
    this.expenseError = null;

    const payload: ExpenseCreateDto = {
      ...this.expenseForm,
      part_id: this.expenseForm.part_id || undefined,
      quantity: this.expenseForm.quantity || undefined,
    };

    const sub = this.financeService.createExpense(payload).subscribe({
      next: () => {
        this.submittingExpense = false;
        this.closeExpenseModal();
        this.loadSummary();
        this.loadExpenses();
      },
      error: (err) => {
        console.error('Error registrando gasto', err);
        this.expenseError = err.error?.detail || 'Error al registrar el gasto';
        this.submittingExpense = false;
      },
    });
    this.subs.add(sub);
  }

  // ========== Helpers ==========
  getPaymentMethodLabel(method: string): string {
    const labels: Record<string, string> = {
      CASH: 'Efectivo',
      CARD: 'Tarjeta',
      TRANSFER: 'Transferencia',
      OTHER: 'Otro',
    };
    return labels[method] || method;
  }

  getCategoryIcon(icon?: string): string {
    return icon || 'category';
  }

  getNetClass(net: number): string {
    if (net > 0) return 'positive';
    if (net < 0) return 'negative';
    return 'neutral';
  }
}
