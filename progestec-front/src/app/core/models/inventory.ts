export interface InventorySummary {
  total_stock: number;
  low_stock_alerts: number;
  movements_today: number;
  critical_parts: number;
  stock_by_category: Record<string, number>;
}

export interface InventoryPart {
  id: number;
  name: string;
  sku?: string | null;
  unit_price: number;
  category?: string | null;
  manufacturer?: string | null;
  compatible_models?: string | null;
  preferred_vendor?: string | null;
  notes?: string | null;
  stock_current: number;
  stock_min: number;
  requires_approval: boolean;
  state: number;
  created_at: string;
  updated_at: string;
  last_movement_at?: string | null;
}

export interface InventoryPartMovement {
  id: number;
  movement_type: 'IN' | 'OUT';
  quantity: number;
  document_ref?: string | null;
  movement_at: string;
  responsible_user_id?: number | null;
  responsible_name?: string | null;
  notes?: string | null;
}

export interface InventoryPartDetail extends InventoryPart {
  movements: InventoryPartMovement[];
}

export interface InventoryFilters {
  search?: string;
  category?: string;
  status?: string;
}

export interface MovementPayload {
  movement_type: 'IN' | 'OUT';
  quantity: number;
  document_ref?: string | null;
  movement_at?: string | null;
  notes?: string | null;
}

export interface InventoryPartPayload {
  name: string;
  sku?: string | null;
  unit_price: number;
  category?: string | null;
  manufacturer?: string | null;
  compatible_models?: string | null;
  preferred_vendor?: string | null;
  notes?: string | null;
  stock_current: number;
  stock_min: number;
  requires_approval: boolean;
}
