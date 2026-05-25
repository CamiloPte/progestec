import { RenderMode, ServerRoute } from '@angular/ssr';

export const serverRoutes: ServerRoute[] = [
  // Rutas con parámetros dinámicos - usar Client render
  {
    path: 'tickets/:id',
    renderMode: RenderMode.Client
  },
  {
    path: 'inventario/:id',
    renderMode: RenderMode.Client
  },
  {
    path: 'facturacion/:id',
    renderMode: RenderMode.Client
  },
  {
    path: 'finanzas/facturas/:id',
    renderMode: RenderMode.Client
  },
  {
    path: 'mis-facturas/:id',
    renderMode: RenderMode.Client
  },
  // Portal del cliente - rutas dinámicas
  {
    path: 'client/tickets/:id',
    renderMode: RenderMode.Client
  },
  {
    path: 'client/devices/:id',
    renderMode: RenderMode.Client
  },
  {
    path: 'client/invoices/:id',
    renderMode: RenderMode.Client
  },
  // Ruta por defecto
  {
    path: '**',
    renderMode: RenderMode.Prerender
  }
];
