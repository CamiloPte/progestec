// src/app/core/config/api.config.ts

/**
 * Detecta automáticamente si estamos en red local o localhost
 * y configura las URLs del API en consecuencia.
 */
function getApiBaseUrl(): string {
  // En SSR (servidor), usar localhost
  if (typeof window === 'undefined') {
    return 'http://localhost:8000';
  }
  
  const hostname = window.location.hostname;
  
  // Si accedemos por IP (red local), usar la misma IP para el API
  if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
    return `http://${hostname}:8000`;
  }
  
  // Por defecto, localhost
  return 'http://localhost:8000';
}

function getCatalogApiUrl(): string {
  if (typeof window === 'undefined') {
    return 'http://localhost:5000';
  }
  
  const hostname = window.location.hostname;
  
  if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
    return `http://${hostname}:5000`;
  }
  
  return 'http://localhost:5000';
}

export const API_BASE_URL = getApiBaseUrl();
export const CATALOG_API_URL = getCatalogApiUrl();
