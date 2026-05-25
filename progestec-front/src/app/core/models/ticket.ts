// src/app/core/models/ticket.ts
import { ISODateString } from './common';
import { TicketStatusRead } from './ticket-status';
import { DeviceReadMinimal } from './device';
import { TicketIssueRead } from './ticket-issue';
import { TicketHistoryRead } from './ticket-history';
import { TicketAttachmentRead } from './ticket-attachment';

export interface TicketReadMinimal {
  id: number;
  tracking_code: string;

  device_id: number;
  assignee_user_id?: number | null;

  status_id: number;
  status_code?: string | null;
  status_name?: string | null;

  // Campos “bonitos” que vienen del backend
  device_label?: string | null;   // ej: "Samsung S21+ 5G – Pantalla verde…"
  assignee_name?: string | null;  // nombre del técnico

  state: number;
  created_at: ISODateString;
  updated_at: ISODateString | null;
}

export interface TicketOwnerInfo {
  id: number;
  full_name?: string | null;
  email: string;
  phone?: string | null;
  identification_type?: string | null;
  identification?: string | null;
  address?: string | null;
}

export interface TicketReadDetail {
  id: number;
  tracking_code: string;

  status: TicketStatusRead;

  assignee_user_id?: number | null;
  assignee_name?: string | null;

  device: DeviceReadMinimal;
  device_label?: string | null;
  owner?: TicketOwnerInfo | null;

  failure_desc: string;
  diagnosis?: string | null;
  cost_estimate?: string | null;   // viene del Decimal como string
  approved_by_owner?: number | null;

  intake_at?: ISODateString | null;
  ready_at?: ISODateString | null;
  delivered_at?: ISODateString | null;
  closed_at?: ISODateString | null;

  issues: TicketIssueRead[];
  history: TicketHistoryRead[];
  attachments: TicketAttachmentRead[];

  state: number;
  created_at: ISODateString;
  updated_at: ISODateString | null;
}
