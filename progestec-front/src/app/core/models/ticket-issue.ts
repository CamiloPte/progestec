// src/app/core/models/ticket-issue.ts
import { ISODateString } from './common';

export interface TicketIssueRead {
    id: number;
    ticket_id: number;
    type: string;
    title: string;
    description?: string | null;
    discovered_at?: ISODateString | null;
    discovered_by?: number | null;
    resolved_at?: ISODateString | null;
    is_primary: number;
    state: number;
    created_at: ISODateString;
    updated_at: ISODateString;
}
