// src/app/core/models/ticket-status.ts
import { ISODateString } from './common';

export interface TicketStatusRead {
    id: number;
    code: string;   // RECEIVED, DIAGNOSING, etc.
    name: string;
    order: number;
    state: number;
    created_at: ISODateString;
    updated_at: ISODateString;
}
