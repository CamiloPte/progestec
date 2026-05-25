# ESTADO ACTUAL DEL PROYECTO - ProGesTec
## Sistema de Gestión de Servicio Técnico

**Fecha de actualización:** Noviembre 2025  
**Versión del sistema:** 1.2.0 (Módulo de Finanzas completo)

---

## 1. RESUMEN EJECUTIVO

ProGesTec es un sistema web desarrollado con **FastAPI (Python)** en el backend y **Angular 20** en el frontend, diseñado para gestionar el servicio técnico de telefonía y laptops. El sistema implementa una arquitectura modular con control de acceso basado en roles (RBAC), gestión completa de tickets, dispositivos, usuarios y un sistema de seguimiento en tiempo real.

### Stack Tecnológico Implementado

**Backend:**
- FastAPI 0.115.12
- SQLAlchemy 2.0.40 (ORM)
- MySQL (Base de datos)
- Alembic (Migraciones)
- JWT (Autenticación)
- Python 3.13

**Frontend:**
- Angular 20.3.0
- TypeScript 5.9.2
- RxJS 7.8.0
- SSR (Server-Side Rendering)

**Infraestructura:**
- Microservicio Express.js (Catálogo de dispositivos)
- Docker (Configurado)
- Sistema de archivos para adjuntos

---

## 2. ESTADO DE IMPLEMENTACIÓN POR OBJETIVO ESPECÍFICO

### OBJETIVO I: Digitalizar el proceso de recepción y diagnóstico de equipos

**Estado:** ✅ **IMPLEMENTADO (85%)**

#### Funcionalidades Completadas:
- ✅ **Creación de tickets** con formulario estructurado
  - Registro de cliente (búsqueda y creación en modal)
  - Registro de dispositivo (búsqueda y creación en modal)
  - Captura de falla reportada
  - Diagnóstico inicial opcional
  - Asignación de técnico
  - Presupuesto estimado
- ✅ **Sistema de tracking** con códigos únicos (`tracking_code`)
- ✅ **Histórico completo** de cambios de estado (timeline)
- ✅ **Sistema de adjuntos** (imágenes y archivos)
  - Subida de archivos al servidor
  - Tipos de adjuntos: intake, diagnosis, status, budget
  - Visualización de imágenes en el detalle del ticket
- ✅ **Modales de creación rápida**:
  - Modal para crear cliente nuevo
  - Modal para crear dispositivo nuevo (con integración al catálogo)
- ✅ **Validaciones por rol** (ADMIN, TECHNICIAN, ADVISOR)

#### Pendiente:
- ⏳ **Pulir UX de búsqueda/overlays**:
  - Búsqueda en vivo mejorada (cliente/dispositivo)
  - Overlays más suaves y responsivos
  - Mostrar teléfono/ID si existe en resultados
  - Evitar errores 422 en guardado
- ⏳ **Comprobante/recibo automático**:
  - Generación de PDF al crear ticket
  - Envío automático por email
  - Formato profesional con logo y datos del servicio

---

### OBJETIVO II: Control de inventarios

**Estado:** ✅ **IMPLEMENTADO (80%)**

#### Funcionalidades Completadas:
- ✅ **Modelo de dispositivos** completo:
  - Relación con usuarios (propietarios)
  - Tipos: PHONE, LAPTOP, TABLET, OTHER
  - Campos: marca, modelo, serial, IMEI
  - Referencias al catálogo externo (manufacturer_id, model_id, variant_id)
  - Foto de ingreso
  - Notas
- ✅ **Dashboard de Inventario**:
  - KPIs: stock total, alertas bajo stock, movimientos hoy, críticos
  - Stock por categoría con barras de progreso
  - Tabla de repuestos con filtros
  - Modal crear/editar repuesto
  - Modal registrar movimiento
- ✅ **Gestión de Repuestos (Parts)**:
  - CRUD completo de repuestos
  - SKU automático
  - Stock actual y mínimo
  - Categorías y fabricantes
  - Compatibilidad con modelos
- ✅ **Movimientos de Inventario**:
  - Entradas (compras, devoluciones)
  - Salidas (uso en tickets, ajustes)
  - Historial de movimientos
  - Actualización automática de stock
- ✅ **Integración con Tickets**:
  - Agregar repuestos usados en ticket
  - Descuento automático de stock
  - Costo de repuestos en factura

#### Pendiente:
- ⏳ **Consumo completo del catálogo externo** (Express.js)
- ⏳ **Alertas automáticas de bajo stock**

---

### OBJETIVO III: Seguimiento de reparaciones

**Estado:** ✅ **IMPLEMENTADO (90%)**

#### Funcionalidades Completadas:
- ✅ **Listado de tickets** con filtros avanzados:
  - Por estado
  - Por técnico asignado
  - Por tipo de dispositivo
  - Por rango de fechas
  - Búsqueda por texto
- ✅ **Dashboard con KPIs**:
  - Total de tickets
  - Tickets abiertos
  - En progreso
  - Tickets cerrados
  - Gráfico de tickets por estado
  - Tabla de tickets recientes
- ✅ **Detalle completo del ticket**:
  - Información del cliente
  - Información del dispositivo
  - Estado actual con chip visual
  - Timeline completo de cambios
  - Adjuntos organizados por tipo
  - Asignación de técnico (con modal)
  - Actualización de estado (con modal y notas)
  - Actualización de diagnóstico (con modal)
  - Actualización de presupuesto (con modal)
- ✅ **Sistema de estados** completo:
  - 7 estados definidos: RECEIVED, DIAGNOSING, WAITING_APPROVAL, REPAIRING, READY, DELIVERED, CLOSED
  - Paleta de colores semántica y consistente
  - Transiciones visibles en timeline
- ✅ **Control de acceso por rol**:
  - ADMIN: acceso total
  - ADVISOR: gestión y asignación
  - TECHNICIAN: solo tickets asignados

#### Pendiente:
- ⏳ **Reglas de flujo por rol**:
  - Validación de transiciones permitidas
  - Aprobación requerida para ciertos cambios
  - Flujo: listo → entregado → cerrado
- ⏳ **SLAs y tiempos**:
  - Tiempo estimado por tipo de reparación
  - Alertas de tickets vencidos
  - Métricas de cumplimiento

---

### OBJETIVO IV: Comunicación con clientes

**Estado:** ✅ **IMPLEMENTADO (85%)**

#### Funcionalidades Completadas:
- ✅ **Portal del Cliente Completo**:
  - Dashboard personalizado con resumen de tickets, dispositivos y facturas
  - Vista de tickets activos con barra de progreso
  - Vista detallada de cada ticket con timeline de historial
  - Historial de dispositivos con servicios asociados
  - Detalle de dispositivo con historial de reparaciones
  - Lista de facturas con estados de pago
  - Descarga de PDFs (recepción, entrega, factura)
  - Perfil del cliente con cambio de contraseña
- ✅ **Aprobar/Rechazar Presupuestos**:
  - Botón de aprobación visible cuando status = WAITING_APPROVAL
  - Notificación visual de presupuestos pendientes
- ✅ **Sistema de usuarios con flag `must_change_password`**:
  - Implementado en modelo y schemas
  - Endpoint para cambio de contraseña
  - Base para forzar cambio en primer login
- ✅ **Diseño Moderno y Minimalista**:
  - Paleta de colores institucional (verde #1a5c3a, dorado #c9a227)
  - Sistema de variables CSS (grays, shadows, radii, transitions)
  - Componente de loading animado (5 tipos LDRS-style)
  - Iconos SVG inline (reemplazo de emojis)
  - Tipografía Inter con jerarquía visual clara
  - Tarjetas con bordes sutiles y sombras modernas
  - Badges con bordes redondeados pill-style
  - Diseño responsive para móviles y tablets
  - Animaciones y transiciones suaves (cubic-bezier)
- ✅ **Filtros de Tickets Funcionales**:
  - Filtro por estado: Todos, En proceso, Finalizados
  - Backend devuelve todos los tickets del cliente
  - Frontend filtra por códigos de estado

#### Rutas del Portal Cliente:
```
/client/dashboard        - Dashboard principal
/client/tickets          - Lista de tickets
/client/tickets/:id      - Detalle del ticket
/client/devices          - Lista de dispositivos
/client/devices/:id      - Detalle del dispositivo
/client/invoices         - Lista de facturas
/client/invoices/:id     - Detalle de factura
/client/profile          - Perfil del usuario
```

#### Pendiente:
- ⏳ **Notificaciones automáticas por email/SMS**:
  - Al recibir equipo (RECEIVED)
  - Al completar diagnóstico (DIAGNOSING)
  - Al requerir aprobación (WAITING_APPROVAL)
  - Al estar listo (READY)
  - Al entregar (DELIVERED)
  - Al cerrar (CLOSED)
- ⏳ **Integración de servicio de email**:
  - SMTP configurado
  - Plantillas HTML para emails
  - Envío asíncrono
- ⏳ **Chatbot Rasa integrado** (Opcional):
  - 40 intents definidos
  - 10 FAQs conectadas a DB
  - Widget moderno en Angular
  - Integración con API de Rasa

---

### OBJETIVO V: Gestión financiera

**Estado:** ✅ **IMPLEMENTADO (90%)**

#### Funcionalidades Completadas:
- ✅ **Módulo de Facturación**:
  - Generación de facturas desde tickets
  - Listado de facturas con filtros
  - Estados: PENDING, PAID, CANCELLED
  - Detalle completo de factura
- ✅ **Sistema de Pagos**:
  - Pagos parciales y totales
  - Múltiples métodos: CASH, CARD, TRANSFER, OTHER
  - Historial de pagos por factura
  - Cálculo automático de saldo pendiente
- ✅ **Módulo de Gastos**:
  - CRUD de gastos operativos
  - 7 categorías predefinidas
  - Asociación con repuestos (compras de inventario)
  - Registro de proveedores
- ✅ **Dashboard Financiero**:
  - Total facturado, cobrado, pendiente
  - Total de gastos
  - Ganancia neta y margen bruto
  - Tendencia mensual (últimos 6 meses)
  - Top clientes por facturación
  - Gastos por categoría

#### Pendiente:
- ⏳ **Reportes financieros avanzados** (PDF)
- ⏳ **Integración con Power BI**

---

### OBJETIVO VI: Seguridad y trazabilidad

**Estado:** ✅ **IMPLEMENTADO (70%)**

#### Funcionalidades Completadas:
- ✅ **Autenticación JWT**:
  - Login seguro
  - Refresh tokens
  - Expiración configurable
- ✅ **Sistema de roles y permisos (RBAC)**:
  - 5 roles: ADMIN, TECHNICIAN, ADVISOR, CLIENT, COURIER
  - Módulos: DASHBOARD, TICKETS, USERS, DEVICES, REPORTS, FINANCE
  - Matriz de permisos por rol
  - Control de acceso en endpoints
- ✅ **Gestión de adjuntos segura**:
  - Almacenamiento en disco
  - Validación de tipos MIME
  - Control de acceso por rol
- ✅ **Arquitectura limpia**:
  - Separación CRUD / Service / Router
  - Manejo centralizado de excepciones
  - Logging estructurado

#### Pendiente:
- ⏳ **Auditoría de cambios (bitácora)**:
  - Tabla de auditoría
  - Registro de cambios en entidades críticas
  - Quién, qué, cuándo, por qué
- ⏳ **Backups y retención**:
  - Estrategia de backups automáticos
  - Política de retención de datos
  - Restauración documentada
- ⏳ **Forzar cambio de contraseña en frontend**:
  - Interceptor que detecta `must_change_password`
  - Modal obligatorio de cambio
  - Redirección después del cambio
- ⏳ **Logs más limpios**:
  - Niveles apropiados (INFO, WARNING, ERROR)
  - Formato estructurado
  - Rotación de logs

---

## 3. FLUJOS POR ROL Y MATRIZ DE PERMISOS

### 3.1 Descripción de Roles

#### 🔴 ADMIN (Administrador)
**Objetivo:** Control total del sistema, gestión de usuarios y configuración.

| Módulo | Acciones | Flujo |
|--------|----------|-------|
| Dashboard | Ver métricas globales | Visión general del negocio |
| Usuarios | CRUD completo | Crear/editar/desactivar usuarios, asignar roles |
| Tickets | Ver todos, reasignar | Supervisar trabajo, reasignar técnicos |
| Dispositivos | Ver todos | Consultar historial de equipos |
| Inventario | CRUD repuestos, movimientos | Gestionar stock, aprobar compras |
| Finanzas | Dashboard, facturas, gastos | Control financiero total |
| Reportes | Todos los reportes | Análisis de negocio |

**Flujo típico:**
```
Login → Dashboard → Revisar métricas → Gestionar usuarios → 
Supervisar tickets → Revisar finanzas → Generar reportes
```

---

#### 🟠 ADVISOR (Asesor de Servicio)
**Objetivo:** Atención al cliente, recepción de equipos, facturación.

| Módulo | Acciones | Flujo |
|--------|----------|-------|
| Dashboard | Ver métricas | Visión del día |
| Tickets | Crear, asignar técnicos | Recibir equipos, crear tickets |
| Dispositivos | Registrar nuevos | Ingresar equipos de clientes |
| Inventario | Ver stock | Consultar disponibilidad |
| Finanzas | Facturar, cobrar, gastos | Generar facturas, registrar pagos |

**Flujo típico:**
```
1. Cliente llega con equipo averiado
2. Asesor crea ticket → Registra dispositivo → Describe falla
3. Asigna técnico disponible
4. Cuando termina: Genera factura → Cobra → Entrega equipo
```

---

#### 🟢 TECHNICIAN (Técnico)
**Objetivo:** Reparar equipos, documentar trabajo, consumir repuestos.

| Módulo | Acciones | Flujo |
|--------|----------|-------|
| Dashboard | Ver sus métricas | Tickets pendientes |
| Tickets | Ver asignados + sin asignar | Trabajar en reparaciones |
| Inventario | Ver stock, consumir | Usar repuestos en reparaciones |

**Flujo típico:**
```
1. Login → Ver tickets pendientes
2. Tomar ticket sin asignar (auto-asignarse) o trabajar en asignado
3. Cambiar estado: "En diagnóstico" → "En reparación"
4. Agregar repuestos usados (se descuenta de inventario)
5. Agregar notas/fotos del trabajo
6. Cambiar estado: "Listo para entrega"
7. Repetir con siguiente ticket
```

**Acciones permitidas en ticket:**
- ✅ Ver detalles
- ✅ Cambiar estado (según flujo permitido)
- ✅ Agregar notas/historial
- ✅ Agregar fotos
- ✅ Agregar repuestos usados
- ✅ Auto-asignarse tickets sin técnico
- ❌ Generar factura
- ❌ Eliminar ticket

---

#### 🔵 CLIENT (Cliente)
**Objetivo:** Seguimiento de sus equipos, ver facturas, historial.

| Módulo | Acciones | Flujo |
|--------|----------|-------|
| Dashboard | Ver sus equipos | Estado de reparaciones |
| Tickets | Ver solo propios | Seguimiento de sus equipos |
| Mis Facturas | Ver, descargar | Consultar pagos |
| Dispositivos | Ver solo propios | Historial de sus equipos |

**Flujo típico:**
```
1. Login → Dashboard muestra estado de sus equipos
2. Ver detalle de ticket → Ver progreso de reparación
3. Consultar historial de facturas
4. Recibir notificación cuando esté listo
```

**Acciones permitidas en ticket:**
- ✅ Ver estado y progreso
- ✅ Ver notas públicas
- ✅ Ver fotos del trabajo
- ❌ Cambiar estado
- ❌ Ver costos internos

---

#### 🟣 COURIER (Domiciliario)
**Objetivo:** Gestionar entregas y recogidas a domicilio.

| Módulo | Acciones | Flujo |
|--------|----------|-------|
| Dashboard | Ver entregas pendientes | Rutas del día |
| Entregas | Lista de recogidas/entregas | Gestionar domicilios |

**Flujo típico:**
```
1. Login → Ver entregas asignadas
2. Marcar recogida completada
3. Marcar entrega completada
4. Registrar novedades si hay
```

---

### 3.2 Matriz de Permisos Detallada

| Acción | ADMIN | ADVISOR | TECHNICIAN | CLIENT | COURIER |
|--------|:-----:|:-------:|:----------:|:------:|:-------:|
| **TICKETS** |||||
| Ver todos | ✅ | ✅ | ❌ | ❌ | ❌ |
| Ver asignados + sin asignar | ✅ | ✅ | ✅ | ❌ | ❌ |
| Ver solo propios (dueño) | ✅ | ✅ | ❌ | ✅ | ❌ |
| Crear ticket | ✅ | ✅ | ❌ | ❌ | ❌ |
| Asignar técnico | ✅ | ✅ | ❌ | ❌ | ❌ |
| Auto-asignarse | ❌ | ❌ | ✅ | ❌ | ❌ |
| Cambiar estado | ✅ | ✅ | ✅* | ❌ | ❌ |
| Agregar repuestos | ✅ | ✅ | ✅ | ❌ | ❌ |
| Agregar notas/fotos | ✅ | ✅ | ✅ | ❌ | ❌ |
| Eliminar ticket | ✅ | ❌ | ❌ | ❌ | ❌ |
| **INVENTARIO** |||||
| Ver stock | ✅ | ✅ | ✅ | ❌ | ❌ |
| Crear repuesto | ✅ | ✅ | ❌ | ❌ | ❌ |
| Registrar movimiento | ✅ | ✅ | ✅ | ❌ | ❌ |
| Eliminar repuesto | ✅ | ❌ | ❌ | ❌ | ❌ |
| **FINANZAS** |||||
| Ver dashboard | ✅ | ✅ | ❌ | ❌ | ❌ |
| Ver facturas | ✅ | ✅ | ❌ | ❌ | ❌ |
| Generar factura | ✅ | ✅ | ❌ | ❌ | ❌ |
| Registrar pago | ✅ | ✅ | ❌ | ❌ | ❌ |
| Registrar gasto | ✅ | ✅ | ❌ | ❌ | ❌ |
| **MIS FACTURAS** |||||
| Ver propias | ❌ | ❌ | ❌ | ✅ | ❌ |
| **USUARIOS** |||||
| CRUD completo | ✅ | ❌ | ❌ | ❌ | ❌ |

*Técnico: Solo estados según flujo (ej: "En diagnóstico" → "En reparación" → "Listo")*

---

### 3.3 Flujo de Estados del Ticket

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   RECEIVED ──► DIAGNOSING ──► WAITING_APPROVAL                 │
│      │              │                │                          │
│      │              │                ▼                          │
│      │              │           REPAIRING                       │
│      │              │                │                          │
│      │              │                ▼                          │
│      │              │      WAITING_PARTS ◄──┐                   │
│      │              │                │      │                   │
│      │              │                ▼      │                   │
│      │              └─────────► READY ──────┘                   │
│      │                            │                             │
│      │                            ▼                             │
│      │                       DELIVERED                          │
│      │                            │                             │
│      │                            ▼                             │
│      │                         CLOSED                           │
│      │                                                          │
│      └───────────► CANCELLED                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Descripción de Estados:**
| Código | Nombre | Descripción |
|--------|--------|-------------|
| RECEIVED | Recibido | Equipo ingresado al sistema |
| DIAGNOSING | En Diagnóstico | Técnico evaluando el problema |
| WAITING_APPROVAL | Esperando Aprobación | Cliente debe aprobar presupuesto |
| REPAIRING | En Reparación | Trabajo en progreso |
| WAITING_PARTS | Esperando Repuestos | Faltan piezas para continuar |
| READY | Listo para Entrega | Reparación completada |
| DELIVERED | Entregado | Cliente recibió su equipo |
| CLOSED | Cerrado | Ticket finalizado |
| CANCELLED | Cancelado | Ticket anulado |

---

## 4. ARQUITECTURA DEL SISTEMA

### 4.1 Backend (FastAPI)

**Estructura de carpetas:**
```
app/
├── api/routes/          # Endpoints REST
│   ├── auth.py         # Autenticación
│   ├── ticket.py        # Gestión de tickets
│   ├── devices.py      # Dispositivos
│   ├── users.py        # Usuarios
│   ├── dashboard.py    # Dashboard y KPIs
│   ├── ticket_status.py # Estados
│   └── modules.py      # Módulos y permisos
├── core/                # Configuración y utilidades
│   ├── config.py       # Variables de entorno
│   ├── security.py     # JWT y hashing
│   ├── roles.py        # Constantes de roles
│   └── exceptions.py   # Manejo de errores
├── models/              # Modelos SQLAlchemy
│   ├── ticket.py
│   ├── device.py
│   ├── user.py
│   └── ...
├── schemas/             # Schemas Pydantic
├── crud/                # Operaciones de base de datos
├── services/            # Lógica de negocio
└── db/                  # Configuración de BD
```

**Endpoints principales:**
- `/api/auth/*` - Autenticación
- `/api/tickets/*` - Tickets
- `/api/devices/*` - Dispositivos
- `/api/users/*` - Usuarios
- `/api/dashboard/*` - Dashboard
- `/api/modules/*` - Módulos y permisos

### 4.2 Frontend (Angular)

**Estructura de carpetas:**
```
progestec-front/src/app/
├── auth/                # Login
├── core/                # Servicios y modelos
│   ├── services/       # Servicios HTTP
│   ├── models/         # Interfaces TypeScript
│   └── layouts/        # Layouts compartidos
├── home/               # Dashboard
├── tickets/            # Módulo de tickets
│   ├── tickets-list/   # Listado
│   ├── ticket-create/  # Creación
│   └── ticket-detail/  # Detalle
└── shared/             # Componentes compartidos
```

**Rutas principales:**
- `/login` - Autenticación
- `/inicio` - Dashboard
- `/tickets` - Listado de tickets
- `/tickets/new` - Crear ticket
- `/tickets/:id` - Detalle de ticket

### 4.3 Base de Datos

**Modelos principales:**
- `users` - Usuarios del sistema
- `roles` - Roles (ADMIN, TECHNICIAN, etc.)
- `modules` - Módulos del sistema
- `module_roles` - Permisos por rol
- `devices` - Dispositivos
- `tickets` - Tickets de servicio
- `ticket_status` - Estados de tickets
- `ticket_history` - Historial de cambios
- `ticket_attachments` - Adjuntos

**Migraciones:**
- Alembic configurado
- Migraciones versionadas
- Historial completo de cambios de esquema

---

## 5. PLAN INMEDIATO (Sprint Actual)

### 5.1 Permisos y Flujos por Rol ✅
**Prioridad:** Alta  
**Estado:** Completado

- [x] ✅ Documentar matriz de permisos por rol
- [x] ✅ Técnico puede ver tickets asignados + sin asignar
- [x] ✅ Cliente puede ver solo sus tickets
- [x] ✅ Guards de rutas en frontend
- [ ] ⏳ Implementar auto-asignación de tickets para técnicos
- [ ] ⏳ Validación de transiciones de estado según rol

### 5.2 Módulo de Finanzas ✅
**Prioridad:** Alta  
**Estado:** Completado

- [x] ✅ Dashboard financiero con KPIs
- [x] ✅ Generación de facturas desde tickets
- [x] ✅ Sistema de pagos (parciales y totales)
- [x] ✅ Gestión de gastos por categorías
- [x] ✅ Tendencia mensual y top clientes
- [x] ✅ Navegación integrada (Ver Facturas, Ver Gastos)

### 5.3 Próximas Mejoras
**Prioridad:** Media  

- [ ] Módulo de Usuarios (CRUD para ADMIN)
- [ ] Módulo de Dispositivos (listado y gestión)
- [ ] Notificaciones por email
- [ ] Reportes exportables (PDF)
- [ ] Integración con Power BI

### 5.4 Microservicio de Catálogo
**Prioridad:** Media  
**Tiempo estimado:** 3-4 días

- [ ] Crear 3 tablas: manufacturers, models, variants
- [ ] Implementar rutas GET en Express
- [ ] Consumir en Angular (módulo dispositivo)
- [ ] Consumir en Angular (módulo ticket)
- [ ] Estandarizar nombres

---

## 5. MÉTRICAS DE PROGRESO

| Objetivo | Progreso | Estado |
|----------|----------|--------|
| I. Recepción/Diagnóstico Digital | 85% | ✅ Implementado |
| II. Control de Inventarios | 80% | ✅ Implementado |
| III. Seguimiento de Reparaciones | 90% | ✅ Implementado |
| IV. Comunicación con Clientes | 75% | ✅ Implementado |
| V. Gestión Financiera | 95% | ✅ Implementado |
| VI. Seguridad y Trazabilidad | 70% | ✅ Implementado |

**Progreso General:** 82.5% completado

---

## 6. PRÓXIMOS PASOS RECOMENDADOS

1. **Implementar notificaciones por email** (Impacto alto)
   - Configurar SMTP
   - Plantillas para cada estado del ticket
   - Envío asíncrono con Celery o similar
2. **Pulir UX del portal cliente** (Impacto medio)
   - Mejorar modales de aprobación de presupuesto
   - Agregar más feedback visual
3. **Forzar cambio de contraseña** (Seguridad)
   - Interceptor en frontend
   - Modal obligatorio
4. **Auditoría de cambios** (Trazabilidad)
   - Registro de acciones críticas
   - Dashboard de auditoría para ADMIN

---

## 7. NOTAS TÉCNICAS

### 7.1 Configuración Actual
- **Base de datos:** MySQL
- **ORM:** SQLAlchemy 2.0
- **Migraciones:** Alembic
- **Autenticación:** JWT con python-jose
- **Validación:** Pydantic 2.11
- **CORS:** Configurado para desarrollo local

### 7.2 Variables de Entorno Requeridas
```env
DATABASE_URL=mysql://user:pass@host/db
SECRET_KEY=tu_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
MEDIA_ROOT=/path/to/uploads
MEDIA_URL=/uploads
```

### 7.3 Comandos Útiles
```bash
# Backend
uvicorn app.main:app --reload

# Frontend
ng serve

# Migraciones
alembic revision --autogenerate -m "descripción"
alembic upgrade head
```

---

**Documento actualizado:** Noviembre 2025  
**Mantenido por:** Equipo de desarrollo ProGesTec

