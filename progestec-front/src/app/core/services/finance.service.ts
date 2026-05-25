import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import { API_BASE_URL } from '../config/api.config';
import {
  FinanceSummary,
  FinanceFilters,
  Expense,
  ExpenseCreateDto,
  ExpenseFilters,
  ExpenseCategory,
  ExpenseCategoryCreateDto,
} from '../models/finance';

@Injectable({ providedIn: 'root' })
export class FinanceService {
  private baseUrl = `${API_BASE_URL}/finances`;

  constructor(private http: HttpClient) {}

  // ========== SUMMARY ==========
  getSummary(filters?: FinanceFilters): Observable<FinanceSummary> {
    let params = new HttpParams();
    if (filters) {
      if (filters.from_date) {
        params = params.set('from_date', filters.from_date);
      }
      if (filters.to_date) {
        params = params.set('to_date', filters.to_date);
      }
      if (filters.include_trends !== undefined) {
        params = params.set('include_trends', String(filters.include_trends));
      }
      if (filters.months_back) {
        params = params.set('months_back', String(filters.months_back));
      }
    }
    return this.http.get<FinanceSummary>(`${this.baseUrl}/summary`, { params });
  }

  // ========== EXPENSE CATEGORIES ==========
  listCategories(): Observable<ExpenseCategory[]> {
    return this.http.get<ExpenseCategory[]>(`${this.baseUrl}/expense-categories`);
  }

  createCategory(payload: ExpenseCategoryCreateDto): Observable<ExpenseCategory> {
    return this.http.post<ExpenseCategory>(`${this.baseUrl}/expense-categories`, payload);
  }

  // ========== EXPENSES ==========
  listExpenses(filters?: ExpenseFilters): Observable<Expense[]> {
    let params = new HttpParams();
    if (filters) {
      if (filters.category_id) {
        params = params.set('category_id', String(filters.category_id));
      }
      if (filters.from_date) {
        params = params.set('from_date', filters.from_date);
      }
      if (filters.to_date) {
        params = params.set('to_date', filters.to_date);
      }
      if (filters.payment_method) {
        params = params.set('payment_method', filters.payment_method);
      }
    }
    return this.http.get<Expense[]>(`${this.baseUrl}/expenses`, { params });
  }

  getExpense(expenseId: number): Observable<Expense> {
    return this.http.get<Expense>(`${this.baseUrl}/expenses/${expenseId}`);
  }

  createExpense(payload: ExpenseCreateDto): Observable<Expense> {
    return this.http.post<Expense>(`${this.baseUrl}/expenses`, payload);
  }

  deleteExpense(expenseId: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/expenses/${expenseId}`);
  }
}
