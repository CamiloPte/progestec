// src/app/core/models/dashboard.ts
import { TicketReadMinimal } from './ticket';

export interface DashboardStatusCount {
  status_code: string;
  status_name?: string | null;
  count: number;
}

export interface DashboardSummary {
  total_tickets: number;
  open_tickets: number;
  in_progress_tickets: number;
  closed_tickets: number;
  by_status: DashboardStatusCount[];
  recent_tickets: TicketReadMinimal[];
}

// ---------- CLIENTE DASHBOARD ----------

export interface ClientTicketSummary {
  id: number;
  tracking_code: string;
  device_label: string;
  status_code: string;
  status_name: string;
  status_color: string;
  progress_percent: number;
  failure_desc: string;
  cost_estimate?: number | null;
  approved_by_owner?: number | null;
  needs_approval: boolean;
  intake_at?: string | null;
  ready_at?: string | null;
  delivered_at?: string | null;
}

export interface ClientDeviceSummary {
  id: number;
  type: string;
  brand: string;
  model: string;
  serial?: string | null;
  tickets_count: number;
  last_service_date?: string | null;
  last_service_status?: string | null;
}

export interface ClientInvoiceSummary {
  id: number;
  invoice_number: string;
  issue_date: string;
  total: number;
  status: string;
  paid_amount: number;
  pending_amount: number;
  ticket_tracking_code?: string | null;
}

export interface ClientNotification {
  type: string;
  icon: string;
  title: string;
  message: string;
  action_url?: string | null;
  created_at: string;
}

export interface ClientDashboardSummary {
  client_name: string;
  active_tickets: number;
  devices_count: number;
  pending_invoices: number;
  pending_approvals: number;
  notifications: ClientNotification[];
  tickets: ClientTicketSummary[];
  devices: ClientDeviceSummary[];
  invoices: ClientInvoiceSummary[];
}
