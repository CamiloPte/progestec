// ========== EXPENSE CATEGORY ==========
export interface ExpenseCategory {
  id: number;
  name: string;
  description?: string;
  icon?: string;
  state: number;
  created_at?: string;
  updated_at?: string;
}

export interface ExpenseCategoryCreateDto {
  name: string;
  description?: string;
  icon?: string;
}

// ========== EXPENSE ==========
export interface Expense {
  id: number;
  category_id: number;
  category_name?: string;
  description: string;
  amount: number;
  payment_method: string;
  reference?: string;
  expense_date: string;
  part_id?: number;
  part_name?: string;
  quantity?: number;
  supplier_name?: string;
  supplier_rut?: string;
  notes?: string;
  created_by_id?: number;
  created_by_name?: string;
  state: number;
  created_at?: string;
  updated_at?: string;
}

export interface ExpenseCreateDto {
  category_id: number;
  description: string;
  amount: number;
  payment_method: string;
  reference?: string;
  expense_date?: string;
  part_id?: number;
  quantity?: number;
  supplier_name?: string;
  supplier_rut?: string;
  notes?: string;
}

export interface ExpenseFilters {
  category_id?: number;
  from_date?: string;
  to_date?: string;
  payment_method?: string;
}

// ========== FINANCE SUMMARY ==========
export interface CategoryExpenseSummary {
  category_id: number;
  category_name: string;
  total: number;
  count: number;
  percentage: number;
}

export interface PeriodMetrics {
  period: string;
  income: number;
  expenses: number;
  net: number;
}

export interface TopClient {
  client_id: number;
  client_name: string;
  total_billed: number;
  invoices_count: number;
}

export interface FinanceSummary {
  from_date?: string;
  to_date?: string;

  // Ingresos
  total_invoiced: number;
  total_collected: number;
  total_pending: number;

  // Contadores de facturas
  invoices_count: number;
  invoices_paid: number;
  invoices_pending: number;

  // Gastos
  total_expenses: number;
  expenses_count: number;
  expenses_by_category: CategoryExpenseSummary[];

  // Márgenes
  gross_profit: number;
  net_profit: number;
  profit_margin: number;

  // Costos
  total_parts_cost: number;
  total_labor_cost: number;

  // Tendencias
  monthly_trend: PeriodMetrics[];

  // Top clientes
  top_clients: TopClient[];
}

export interface FinanceFilters {
  from_date?: string;
  to_date?: string;
  include_trends?: boolean;
  months_back?: number;
}
