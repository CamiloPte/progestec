import { ISODateString } from './common';

export interface TicketAttachmentRead {
  id: number;
  ticket_id: number;
  history_id?: number | null;
  attachment_type: string;
  original_name: string;
  stored_name: string;
  file_url: string;
  mime_type?: string | null;
  file_size?: number | null;
  note?: string | null;
  uploaded_by?: number | null;
  created_at: ISODateString;
  updated_at: ISODateString | null;
  state: number;
}
