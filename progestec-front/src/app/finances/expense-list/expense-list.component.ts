import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { Subscription } from 'rxjs';

import { AuthenticatedLayoutComponent } from '../../core/layouts/authenticated-layout.component';
import { FinanceService } from '../../core/services/finance.service';
import { Expense, ExpenseCategory, ExpenseCreateDto } from '../../core/models/finance';
import { InventoryService } from '../../core/services/inventory.service';

@Component({
  selector: 'app-expense-list',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule, AuthenticatedLayoutComponent],
  templateUrl: './expense-list.component.html',
  styleUrls: ['./expense-list.component.css'],
})
export class ExpenseListComponent implements OnInit, OnDestroy {
  expenses: Expense[] = [];
  categories: ExpenseCategory[] = [];
  parts: any[] = [];

  loading = true;
  error: string | null = null;

  filters = {
    category_id: '',
    payment_method: '',
    from_date: '',
    to_date: '',
  };

  // Modal
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
    this.loadExpenses();
    this.loadCategories();
  }

  ngOnDestroy(): void {
    this.subs.unsubscribe();
  }

  loadExpenses(): void {
    this.loading = true;
    this.error = null;

    const params: any = {};
    if (this.filters.category_id) {
      params.category_id = Number(this.filters.category_id);
    }
    if (this.filters.payment_method) {
      params.payment_method = this.filters.payment_method;
    }
    if (this.filters.from_date) {
      params.from_date = this.filters.from_date;
    }
    if (this.filters.to_date) {
      params.to_date = this.filters.to_date;
    }

    const sub = this.financeService.listExpenses(params).subscribe({
      next: (data) => {
        this.expenses = data;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error cargando gastos', err);
        this.error = 'No se pudieron cargar los gastos.';
        this.loading = false;
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
    this.loadExpenses();
  }

  clearFilters(): void {
    this.filters = {
      category_id: '',
      payment_method: '',
      from_date: '',
      to_date: '',
    };
    this.loadExpenses();
  }

  // ========== Modal ==========
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

  deleteExpense(expense: Expense): void {
    if (!confirm(`¿Eliminar el gasto "${expense.description}"?`)) {
      return;
    }

    const sub = this.financeService.deleteExpense(expense.id).subscribe({
      next: () => {
        this.loadExpenses();
      },
      error: (err) => {
        console.error('Error eliminando gasto', err);
        alert('Error al eliminar el gasto');
      },
    });
    this.subs.add(sub);
  }

  // Helpers
  getPaymentMethodLabel(method: string): string {
    const labels: Record<string, string> = {
      CASH: 'Efectivo',
      CARD: 'Tarjeta',
      TRANSFER: 'Transferencia',
      OTHER: 'Otro',
    };
    return labels[method] || method;
  }

  getTotalExpenses(): number {
    return this.expenses.reduce((sum, exp) => sum + exp.amount, 0);
  }
}
