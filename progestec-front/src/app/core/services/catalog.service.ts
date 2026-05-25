import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { CATALOG_API_URL } from '../config/api.config';
import { CatalogManufacturer, CatalogModel, CatalogVariant } from '../models/catalog';

@Injectable({
  providedIn: 'root',
})
export class CatalogService {
  private readonly baseUrl = CATALOG_API_URL;

  constructor(private http: HttpClient) {}

  getManufacturers(): Observable<CatalogManufacturer[]> {
    return this.http.get<CatalogManufacturer[]>(`${this.baseUrl}/manufacturers`);
  }

  getModels(manufacturerId: number): Observable<CatalogModel[]> {
    return this.http.get<CatalogModel[]>(`${this.baseUrl}/models`, {
      params: { manufacturer_id: manufacturerId },
    });
  }

  getVariants(modelId: number): Observable<CatalogVariant[]> {
    return this.http.get<CatalogVariant[]>(`${this.baseUrl}/variants`, {
      params: { model_id: modelId },
    });
  }
}
