// Catálogo de fabricantes, modelos y variantes del microservicio Express
import { ISODateString } from './common';

export interface CatalogManufacturer {
  id: number;
  name: string;
  country?: string | null;
  created_at: ISODateString;
}

export interface CatalogModel {
  id: number;
  manufacturer_id: number;
  name: string;
  category?: string | null; // PHONE, LAPTOP, TABLET, etc.
  released_year?: number | null;
  created_at: ISODateString;
}

export interface CatalogVariant {
  id: number;
  model_id: number;
  variant_name?: string | null;
  sku?: string | null;
  storage_gb?: number | null;
  ram_gb?: number | null;
  color?: string | null;
  notes?: string | null;
  created_at: ISODateString;
}
