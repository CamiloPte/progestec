// src/app/core/models/device.ts
import { ISODateString } from './common';

export interface DeviceReadMinimal {

    id: number;
    owner_user_id: number;
    type: string;     // PHONE | LAPTOP | TABLET | OTHER
    brand: string;
    model: string;
    serial?: string | null;
    imei?: string | null;
    catalog_manufacturer_id?: number | null;
    catalog_model_id?: number | null;
    catalog_variant_id?: number | null;
    state: number;
    created_at: ISODateString;
    updated_at: ISODateString;
}
