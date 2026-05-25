import { ISODateString } from './common';

export interface InvoicePayment {
  id: number;
  invoice_id: number;
  amount: number;
  payment_method: string;
  reference?: string | null;
  paid_at: ISODateString;
  created_by_id?: number | null;
  created_by_name?: string | null;
  state: number;
  created_at?: ISODateString;
  updated_at?: ISODateString | null;
}

export interface Invoice {
  id: number;
  ticket_id: number;
  client_id: number;
  invoice_number: string;
  issue_date: ISODateString;
  due_date?: ISODateString | null;

  parts_cost: number;
  labor_cost: number;
  discount_amount: number;
  subtotal: number;
  tax_percentage: number;
  tax_amount: number;
  total: number;

  status: string;
  total_paid: number;
  outstanding_amount: number;
  paid_at?: ISODateString | null;
  notes?: string | null;

  ticket_tracking_code?: string | null;
  client_name?: string | null;

  payments: InvoicePayment[];
}

export interface InvoiceCreateDto {
  labor_cost: number;
  discount_amount?: number;
  tax_percentage?: number;
  due_date?: ISODateString | null;
  notes?: string;
  issue_date?: ISODateString | null;
}

export interface InvoiceUpdateDto {
  labor_cost?: number;
  discount_amount?: number;
  tax_percentage?: number;
  due_date?: ISODateString | null;
  notes?: string;
  confirm?: boolean;  // Si es true, cambia de DRAFT a PENDING
}

export interface InvoicePaymentCreateDto {
  amount: number;
  payment_method: string;
  reference?: string | null;
  paid_at?: ISODateString | null;
}

export interface InvoiceFilters {
  status?: string[];
  client_id?: number;
  from_date?: ISODateString;
  to_date?: ISODateString;
  with_debt?: boolean;
  ticket_id?: number;
}
