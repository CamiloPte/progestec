// src/app/core/models/ticket-history.ts
import { ISODateString } from './common';

export interface TicketHistoryRead {
  id: number;
  ticket_id: number;
  status_id: number;
  user_id?: number | null;
  note?: string | null;
  created_at: ISODateString;
  state: number;
  status_name?: string | null;
  status_code?: string | null;
  user_name?: string | null;
}
