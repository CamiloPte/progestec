import { ISODateString } from './common';

export interface TicketPartRead {
  id: number;
  ticket_id: number;
  part_id: number;
  qty: number;
  unit_price_snapshot: number | string;
  total_cost: number | string;
  created_by_id?: number | null;
  created_at: ISODateString;
  state: number;
  part_name?: string | null;
  part_sku?: string | null;
}

export interface TicketPartCreate {
  part_id: number;
  qty: number;
  unit_price_snapshot?: number | null;
  notes?: string | null;
}
