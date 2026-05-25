# PROYECTO DE GRADO
## Prototipo de Software para la Gestión del Servicio Técnico de Telefonía y Laptops en Barranquilla

**ProGesTec - Sistema de Gestión de Servicio Técnico**

---

## INTRODUCCIÓN

En los últimos años, los centros de servicio técnico para dispositivos electrónicos han enfrentado grandes desafíos debido a la ausencia de sistemas digitales que faciliten la organización, el control y la trazabilidad de sus procesos. Esta situación repercute en la eficiencia interna, la calidad del servicio y la satisfacción del cliente. El caso particular de Fedecafé en Barranquilla refleja estas dificultades: el servicio técnico opera sin una plataforma estructurada, lo que genera retrasos, errores y confusión tanto en la atención a los clientes como en la gestión de inventarios y finanzas.

Ante esta problemática, se ha desarrollado **ProGesTec**, un prototipo de software web que integra módulos para recepción de equipos, control de inventarios, seguimiento de reparaciones, comunicación con clientes y administración financiera. Con ello se busca optimizar la eficiencia operativa, minimizar errores y mejorar la experiencia de los usuarios, contribuyendo a la modernización y transformación digital del sector de servicios técnicos.

---

## OBJETIVOS

### Objetivo General

Desarrollar un prototipo de software para la gestión del servicio técnico de telefonía y laptops en Barranquilla, con el fin de optimizar la organización de procesos internos y mejorar la experiencia del cliente.

### Objetivos Específicos

#### I. Digitalizar el proceso de recepción y diagnóstico de equipos

**Estado:** ✅ **85% Completado**

**Implementado:**
- Sistema de creación de tickets con formularios estructurados
- Registro de clientes y dispositivos con modales de creación rápida
- Captura de falla reportada y diagnóstico inicial
- Sistema de tracking con códigos únicos
- Histórico completo de cambios (timeline)
- Sistema de adjuntos (imágenes y archivos)
- Asignación de técnicos y presupuestos

**Pendiente:**
- Generación automática de comprobantes en PDF
- Envío automático de recibos por correo electrónico
- Mejoras en UX de búsqueda y validaciones

#### II. Implementar un sistema de control de inventarios

**Estado:** ⚠️ **40% Completado**

**Implementado:**
- Modelo completo de dispositivos con relación a propietarios
- Catálogo de dispositivos (marca, modelo, variante)
- Referencias a catálogo externo
- Microservicio Express.js para catálogo (estructura base)

**Pendiente:**
- Módulo de repuestos y control de stock
- Alertas automáticas de bajo inventario
- Integración completa con catálogo externo
- Registro en tiempo real de movimientos

#### III. Desarrollar un módulo de seguimiento de reparaciones

**Estado:** ✅ **90% Completado**

**Implementado:**
- Tableros de estado con KPIs en tiempo real
- Listado de tickets con filtros avanzados
- Detalle completo con timeline de cambios
- Bitácoras por dispositivo con historial completo
- Sistema de 7 estados con transiciones visibles
- Control de acceso por rol (ADMIN, TECHNICIAN, ADVISOR)

**Pendiente:**
- Reglas de flujo por rol (validación de transiciones)
- SLAs y tiempos estimados de reparación
- Vistas especializadas por técnico y cliente

#### IV. Mejorar la comunicación con los clientes

**Estado:** ⚠️ **20% Completado**

**Implementado:**
- Sistema de usuarios con flag de cambio de contraseña obligatorio
- Estructura base para notificaciones

**Pendiente:**
- Notificaciones automáticas por correo electrónico en hitos clave:
  - Recepción del equipo
  - Completado de diagnóstico
  - Requerimiento de aprobación
  - Equipo listo para entrega
  - Entrega al cliente
  - Cierre del ticket
- Integración de SMS para notificaciones críticas
- Chatbot Rasa con 40 intents y FAQs conectadas a base de datos

#### V. Optimizar la gestión financiera del servicio

**Estado:** ❌ **0% Completado**

**Pendiente:**
- Módulo de finanzas con registro de ingresos y egresos
- Facturación simple integrada con tickets
- Reportes contables y de rentabilidad
- Integración con Power BI para visualización analítica:
  - 4 KPIs principales
  - 6 gráficos analíticos
  - Filtros interactivos

#### VI. Asegurar la seguridad y trazabilidad de la información

**Estado:** ✅ **70% Completado**

**Implementado:**
- Sistema de autenticación JWT
- Control de acceso basado en roles (RBAC)
- 5 roles definidos: ADMIN, TECHNICIAN, ADVISOR, CLIENT, COURIER
- 6 módulos con permisos granulares
- Almacenamiento seguro de adjuntos
- Arquitectura limpia con separación de responsabilidades
- Manejo centralizado de excepciones

**Pendiente:**
- Sistema de auditoría completo (bitácora de cambios)
- Backups automáticos y política de retención
- Forzar cambio de contraseña en primer login (frontend)
- Logs estructurados con rotación

---

## MARCO TEÓRICO / ESTADO DEL ARTE

### Tecnologías Utilizadas

**Backend:**
- **FastAPI:** Framework web moderno y rápido para Python, con soporte nativo para async/await y documentación automática (OpenAPI/Swagger).
- **SQLAlchemy 2.0:** ORM (Object-Relational Mapping) que facilita la interacción con la base de datos MySQL de forma segura y eficiente.
- **Pydantic:** Validación de datos y serialización con tipos seguros.
- **Alembic:** Sistema de migraciones de base de datos versionado.

**Frontend:**
- **Angular 20:** Framework de desarrollo frontend con arquitectura basada en componentes, servicios y módulos.
- **TypeScript:** Superset de JavaScript con tipado estático para mayor seguridad en el código.
- **RxJS:** Programación reactiva para manejo de flujos de datos asíncronos.

**Arquitectura:**
- **Arquitectura en capas:** Separación clara entre presentación (API routes), lógica de negocio (services), acceso a datos (CRUD) y modelos.
- **Microservicios:** Catálogo de dispositivos como servicio independiente (Express.js).
- **RESTful API:** Interfaz de programación siguiendo principios REST.

### Referentes y Casos Similares

- **ServiceNow:** Plataforma de gestión de servicios IT con módulos de tickets y seguimiento.
- **Zendesk:** Sistema de gestión de tickets y atención al cliente.
- **RepairShopr:** Software específico para talleres de reparación de dispositivos.

**Diferenciadores de ProGesTec:**
- Enfoque específico en servicio técnico de dispositivos móviles y laptops
- Integración con catálogo externo de dispositivos
- Sistema de roles adaptado al contexto de talleres técnicos
- Portal para clientes con seguimiento en tiempo real

---

## METODOLOGÍA

### Enfoque y Tipo de Estudio

El proyecto se aborda desde un **enfoque mixto (cualitativo-cuantitativo)**, ya que combina la percepción de los actores involucrados con datos cuantificables sobre el funcionamiento del servicio técnico. Se clasifica como una **investigación aplicada**, porque busca ofrecer una solución tecnológica concreta a una problemática real de la organización, y de tipo **descriptivo-propositivo**, al caracterizar la situación actual y plantear el diseño de un sistema que la mejore.

### Población, Muestra y Contexto de Estudio

**Población de referencia:**
- Personal técnico y administrativo del servicio técnico de Fedecafé Barranquilla
- Clientes usuarios del servicio técnico

**Muestra intencional:**
- Personal técnico y de apoyo administrativo (procesos internos, flujos de trabajo)
- Clientes (percepción sobre tiempos, comunicación, satisfacción)

**Contexto:** Área de servicio técnico de Fedecafé Barranquilla

### Técnicas e Instrumentos de Recolección de Información

**Fase diagnóstica:**
- Revisión documental: análisis de formatos existentes (órdenes de servicio, planillas, comprobantes)
- Entrevistas semiestructuradas al personal técnico y administrativo
- Encuestas estructuradas aplicadas a clientes

### Procedimiento Metodológico

#### 1. Diagnóstico y Análisis de la Situación Actual ✅

**Completado:**
- Levantamiento de información mediante observación y entrevistas
- Identificación de problemas clave:
  - Desorganización de registros
  - Falta de trazabilidad
  - Dificultades en control de inventarios
  - Problemas en seguimiento de reparaciones

#### 2. Especificación de Requisitos del Sistema ✅

**Completado:**
- Definición de procesos automatizados:
  - Recepción de equipos ✅
  - Diagnóstico ✅
  - Reparaciones ✅
  - Manejo de inventario ⚠️ (parcial)
  - Reportes ⚠️ (pendiente)
  - Entregas ✅
- Elaboración de casos de uso y actores
- Requerimientos funcionales y no funcionales definidos

#### 3. Diseño del Sistema ✅

**Completado:**
- Arquitectura general del software:
  - Backend: FastAPI con arquitectura en capas
  - Frontend: Angular con componentes modulares
  - Base de datos: MySQL con SQLAlchemy ORM
- Modelado de base de datos:
  - 15+ entidades principales definidas
  - Relaciones y atributos especificados
  - Migraciones versionadas con Alembic
- Diseño de interfaz de usuario:
  - Pantallas para recepción de equipos ✅
  - Seguimiento de órdenes ✅
  - Gestión de inventarios ⚠️ (parcial)
  - Reportes administrativos ❌ (pendiente)

#### 4. Desarrollo del Prototipo de Software ⚠️

**Estado actual:** Desarrollo incremental en progreso

**Módulos implementados:**
- ✅ Autenticación y autorización
- ✅ Gestión de usuarios y roles
- ✅ Recepción y creación de tickets
- ✅ Seguimiento de reparaciones
- ✅ Dashboard con KPIs
- ✅ Gestión de dispositivos (básico)
- ⚠️ Control de inventarios (parcial)
- ❌ Gestión financiera (pendiente)
- ❌ Reportes avanzados (pendiente)

**Metodología de desarrollo:**
- Desarrollo incremental basado en prototipos
- Versiones funcionales parciales
- Retroalimentación continua
- Integración gradual de funcionalidades

---

## RESULTADOS OBTENIDOS

### Funcionalidades Implementadas

1. **Sistema de Autenticación y Autorización**
   - Login seguro con JWT
   - 5 roles con permisos granulares
   - Control de acceso por módulo

2. **Gestión de Tickets**
   - Creación con formularios estructurados
   - Tracking único por ticket
   - 7 estados con transiciones visibles
   - Timeline completo de cambios
   - Sistema de adjuntos

3. **Dashboard Analítico**
   - KPIs en tiempo real
   - Gráficos de tickets por estado
   - Tabla de tickets recientes

4. **Gestión de Dispositivos**
   - Registro de dispositivos
   - Relación con propietarios
   - Integración con catálogo externo (parcial)

5. **Gestión de Usuarios**
   - CRUD completo
   - Asignación de roles
   - Control de permisos

### Métricas de Progreso

| Módulo | Progreso | Estado |
|--------|----------|--------|
| Autenticación | 100% | ✅ Completo |
| Tickets | 90% | ✅ Completo |
| Dashboard | 100% | ✅ Completo |
| Dispositivos | 60% | ⚠️ Parcial |
| Inventario | 40% | ⚠️ Parcial |
| Finanzas | 0% | ❌ Pendiente |
| Reportes | 0% | ❌ Pendiente |
| Notificaciones | 20% | ⚠️ Parcial |

**Progreso General del Prototipo:** 51%

---

## PLAN DE TRABAJO INMEDIATO

### Sprint 1: Mejoras de UX y Catálogo (1-2 semanas)

1. **UX Creación de Ticket**
   - Búsqueda en vivo mejorada
   - Overlays más suaves
   - Validaciones en tiempo real

2. **Microservicio de Catálogo**
   - Implementar 3 tablas (manufacturers, models, variants)
   - Rutas GET en Express.js
   - Integración en Angular

### Sprint 2: Notificaciones y Finanzas (2-3 semanas)

1. **Sistema de Notificaciones**
   - Integración de email (SMTP)
   - Plantillas HTML
   - Notificaciones en hitos clave

2. **Módulo de Finanzas**
   - Modelo de ingresos/egresos
   - Facturación simple
   - Reportes básicos

### Sprint 3: Reportes y Chatbot (2-3 semanas)

1. **Power BI**
   - Dataset de tickets
   - KPIs y gráficos
   - Embebido en módulo Reportes

2. **Chatbot Rasa**
   - 40 intents
   - 10 FAQs
   - Widget en Angular

---

## CONCLUSIONES PARCIALES

El desarrollo del prototipo ProGesTec ha avanzado significativamente en los módulos core del sistema. Se ha logrado implementar una base sólida con autenticación, gestión de tickets, seguimiento de reparaciones y dashboard analítico. La arquitectura implementada permite escalabilidad y mantenibilidad del sistema.

Los próximos pasos críticos incluyen la finalización del módulo de inventarios, implementación de notificaciones automáticas, desarrollo del módulo financiero e integración de herramientas de analítica y comunicación con clientes.

El sistema demuestra viabilidad técnica y funcional para resolver las problemáticas identificadas en el servicio técnico, con un progreso del 51% hacia la completitud del prototipo.

---

**Versión del documento:** 1.0  
**Fecha de actualización:** Enero 2025  
**Estado del proyecto:** En desarrollo activo

