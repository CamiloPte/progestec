import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { API_BASE_URL } from '../config/api.config';
import { DeviceReadMinimal } from '../models/device';

@Injectable({
  providedIn: 'root',
})
export class DeviceService {
  private readonly baseUrl = `${API_BASE_URL}`;

  constructor(private http: HttpClient) {}

  listDevices(): Observable<DeviceReadMinimal[]> {
    return this.http.get<DeviceReadMinimal[]>(`${this.baseUrl}/devices`);
  }

  listDevicesByClient(clientId: number): Observable<DeviceReadMinimal[]> {
    return this.http.get<DeviceReadMinimal[]>(`${this.baseUrl}/clients/${clientId}/devices`);
  }

  quickCreateDevice(payload: {
    owner_user_id: number;
    type: string;
    brand: string;
    model: string;
    serial?: string | null;
    imei?: string | null;
    notes?: string | null;
    intake_photo_file?: File | null;
    catalog_manufacturer_id?: number | null;
    catalog_model_id?: number | null;
    catalog_variant_id?: number | null;
  }): Observable<DeviceReadMinimal> {
    const formData = new FormData();
    formData.append('owner_user_id', String(payload.owner_user_id));
    formData.append('type', payload.type);
    formData.append('brand', payload.brand);
    formData.append('model', payload.model);
    if (payload.serial) formData.append('serial', payload.serial);
    if (payload.imei) formData.append('imei', payload.imei);
    if (payload.notes) formData.append('notes', payload.notes);
    if (payload.catalog_manufacturer_id) {
      formData.append('catalog_manufacturer_id', String(payload.catalog_manufacturer_id));
    }
    if (payload.catalog_model_id) {
      formData.append('catalog_model_id', String(payload.catalog_model_id));
    }
    if (payload.catalog_variant_id) {
      formData.append('catalog_variant_id', String(payload.catalog_variant_id));
    }
    if (payload.intake_photo_file) {
      formData.append('intake_photo', payload.intake_photo_file);
    }
    return this.http.post<DeviceReadMinimal>(`${this.baseUrl}/devices/quick`, formData);
  }
}
