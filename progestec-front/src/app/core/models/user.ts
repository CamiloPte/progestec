// src/app/core/models/user.ts

export interface CurrentUser {
  id: number;
  email: string;
  full_name: string;
  phone: string | null;
  identification?: string | null;
  identification_type?: string | null;

  role_name?: string;
  role?: {
    id: number;
    name: string;
  };
  modules?: string[];
}

export interface UserReadMinimal {
  id: number;
  full_name: string;
  email: string;
  role_name?: string | null;
  phone?: string | null;
  identification?: string | null;
  identification_type?: string | null;
  role_id?: number;
  state?: number;
  must_change_password?: boolean;
  modules?: string[];
  created_at?: string;
  updated_at?: string;
}

export interface UserReadDetail extends UserReadMinimal {}

export interface UserCreate {
  full_name: string;
  email: string;
  password: string;
  identification: string;
  phone: string;
  identification_type?: string | null;
  role_id: number;
}

export interface UserUpdate {
  full_name?: string;
  phone?: string;
  identification_type?: string;
  role_id?: number;
}
