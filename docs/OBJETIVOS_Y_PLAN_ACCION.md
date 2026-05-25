# OBJETIVOS ESPECÍFICOS Y PLAN DE ACCIÓN
## ProGesTec - Próximos Pasos

---

## OBJETIVOS PRIORITARIOS

### 🎯 Objetivo 1: Mejorar UX de Creación de Ticket
**Prioridad:** 🔴 Alta  
**Impacto:** Alto  
**Esfuerzo:** Bajo-Medio  
**Tiempo estimado:** 2-3 días

#### Tareas Específicas:

1. **Búsqueda en vivo mejorada**
   - [ ] Implementar debounce en búsqueda de clientes
   - [ ] Mostrar resultados mientras se escribe
   - [ ] Highlight de coincidencias
   - [ ] Mostrar teléfono e ID si existe en resultados
   - [ ] Indicador de carga durante búsqueda

2. **Overlays más suaves**
   - [ ] Mejorar animaciones de modales
   - [ ] Ajustar z-index y backdrop
   - [ ] Hacer modales más responsivos
   - [ ] Mejorar scroll interno en modales largos

3. **Validaciones en tiempo real**
   - [ ] Validar campos mientras se escribe
   - [ ] Mensajes de error contextuales
   - [ ] Prevenir envío con datos inválidos
   - [ ] Evitar errores 422 en guardado

4. **Mejoras visuales**
   - [ ] Mejor feedback visual en acciones
   - [ ] Estados de carga más claros
   - [ ] Mensajes de éxito/error mejorados

**Archivos a modificar:**
- `progestec-front/src/app/tickets/ticket-create/ticket-create.component.ts`
- `progestec-front/src/app/tickets/ticket-create/ticket-create.component.html`
- `progestec-front/src/app/tickets/ticket-create/ticket-create.component.css`

---

### 🎯 Objetivo 2: Completar Microservicio de Catálogo
**Prioridad:** 🔴 Alta  
**Impacto:** Alto  
**Esfuerzo:** Medio  
**Tiempo estimado:** 3-4 días

#### Tareas Específicas:

1. **Base de datos del catálogo**
   - [ ] Crear tabla `manufacturers` (id, name, created_at, updated_at)
   - [ ] Crear tabla `models` (id, manufacturer_id, name, created_at, updated_at)
   - [ ] Crear tabla `variants` (id, model_id, variant_name, storage_gb, ram_gb, color, created_at, updated_at)
   - [ ] Crear relaciones y foreign keys
   - [ ] Poblar con datos iniciales (Samsung, Apple, etc.)

2. **API Express.js**
   - [ ] GET `/api/manufacturers` - Listar fabricantes
   - [ ] GET `/api/manufacturers/:id/models` - Modelos por fabricante
   - [ ] GET `/api/models/:id/variants` - Variantes por modelo
   - [ ] GET `/api/models/:id` - Detalle de modelo
   - [ ] Middleware de CORS
   - [ ] Manejo de errores

3. **Integración en Angular**
   - [ ] Servicio para consumir API del catálogo
   - [ ] Integrar en modal de creación de dispositivo
   - [ ] Integrar en formulario de ticket
   - [ ] Caché de resultados
   - [ ] Manejo de errores y estados de carga

**Archivos a crear/modificar:**
- `catalog-service/src/server.js` (completar)
- `catalog-service/src/db.js` (nuevo)
- `catalog-service/src/routes/catalog.js` (nuevo)
- `progestec-front/src/app/core/services/catalog.service.ts` (nuevo)
- `progestec-front/src/app/tickets/ticket-create/ticket-create.component.ts` (modificar)

---

### 🎯 Objetivo 3: Implementar Power BI
**Prioridad:** 🟡 Media  
**Impacto:** Medio  
**Esfuerzo:** Alto  
**Tiempo estimado:** 4-5 días

#### Tareas Específicas:

1. **Preparación de datos**
   - [ ] Definir dataset: tickets, estados, tiempos, dispositivos
   - [ ] Crear vista SQL o endpoint API para Power BI
   - [ ] Configurar conexión a base de datos MySQL
   - [ ] Validar calidad de datos

2. **KPIs principales (4)**
   - [ ] KPI 1: Total de tickets activos
   - [ ] KPI 2: Tiempo promedio de reparación
   - [ ] KPI 3: Tasa de tickets cerrados
   - [ ] KPI 4: Satisfacción del cliente (si aplica)

3. **Gráficos analíticos (6)**
   - [ ] Gráfico 1: Tickets por estado (barras)
   - [ ] Gráfico 2: Evolución temporal de tickets (línea)
   - [ ] Gráfico 3: Distribución por tipo de dispositivo (pie)
   - [ ] Gráfico 4: Rendimiento por técnico (barras horizontales)
   - [ ] Gráfico 5: Tiempos promedio por estado (barras)
   - [ ] Gráfico 6: Tickets por mes (columnas)

4. **Filtros interactivos (1)**
   - [ ] Filtro por rango de fechas
   - [ ] Filtro por técnico
   - [ ] Filtro por tipo de dispositivo
   - [ ] Filtro por estado

5. **Publicación e integración**
   - [ ] Publicar reporte en Power BI Service
   - [ ] Configurar actualización automática
   - [ ] Obtener URL de embed
   - [ ] Crear componente Angular para embebido
   - [ ] Integrar en módulo "Reportes"

**Archivos a crear:**
- `docs/power-bi-spec.md` (especificación)
- `progestec-front/src/app/reports/reports.component.ts` (nuevo)
- `progestec-front/src/app/reports/reports.component.html` (nuevo)

---

### 🎯 Objetivo 4: Integrar Chatbot Rasa
**Prioridad:** 🟡 Media  
**Impacto:** Medio  
**Esfuerzo:** Alto  
**Tiempo estimado:** 5-7 días

#### Tareas Específicas:

1. **Configuración de Rasa**
   - [ ] Instalar Rasa Open Source
   - [ ] Crear proyecto Rasa
   - [ ] Configurar `config.yml` con pipeline
   - [ ] Configurar `domain.yml` con intents y respuestas

2. **Definir 40 intents**
   - [ ] Categorías: Estado de ticket, Información de dispositivo, Horarios, Costos, etc.
   - [ ] Ejemplos de entrenamiento por intent
   - [ ] Entrenar modelo
   - [ ] Evaluar precisión

3. **10 FAQs conectadas a DB**
   - [ ] Crear tabla `faqs` en base de datos
   - [ ] Poblar con preguntas frecuentes
   - [ ] Endpoint API para consultar FAQs
   - [ ] Integrar en Rasa con custom action
   - [ ] Probar respuestas dinámicas

4. **Widget en Angular**
   - [ ] Crear componente de chat
   - [ ] Diseño moderno y responsivo
   - [ ] Integrar con API de Rasa
   - [ ] Manejar estados: typing, sent, received
   - [ ] Historial de conversación
   - [ ] Botón flotante para abrir/cerrar

5. **Testing y ajustes**
   - [ ] Probar todos los intents
   - [ ] Ajustar respuestas
   - [ ] Mejorar precisión del modelo
   - [ ] Optimizar tiempos de respuesta

**Archivos a crear:**
- `rasa-bot/` (directorio completo del proyecto Rasa)
- `progestec-front/src/app/shared/chatbot/chatbot.component.ts` (nuevo)
- `progestec-front/src/app/shared/chatbot/chatbot.component.html` (nuevo)
- `progestec-front/src/app/shared/chatbot/chatbot.component.css` (nuevo)
- `app/models/faq.py` (nuevo)
- `app/api/routes/faq.py` (nuevo)

---

### 🎯 Objetivo 5: Limpieza de Código
**Prioridad:** 🟢 Baja  
**Impacto:** Bajo  
**Esfuerzo:** Bajo  
**Tiempo estimado:** 2 días

#### Tareas Específicas:

1. **Comentarios**
   - [ ] Revisar todos los archivos Python
   - [ ] Agregar docstrings breves en funciones complejas
   - [ ] Remover comentarios extensos obsoletos
   - [ ] Estandarizar formato de comentarios

2. **TypeScript/Angular**
   - [ ] Revisar componentes TypeScript
   - [ ] Agregar comentarios JSDoc donde sea necesario
   - [ ] Remover console.log de producción
   - [ ] Limpiar imports no usados

3. **Organización**
   - [ ] Verificar estructura de carpetas
   - [ ] Estandarizar nombres de archivos
   - [ ] Agrupar funciones relacionadas
   - [ ] Documentar arquitectura en README

**Archivos a revisar:**
- Todos los archivos `.py` en `app/`
- Todos los archivos `.ts` en `progestec-front/src/app/`

---

## PLAN DE EJECUCIÓN SUGERIDO

### Semana 1-2: UX y Catálogo
- Días 1-3: Mejorar UX de creación de ticket
- Días 4-7: Completar microservicio de catálogo

### Semana 3-4: Power BI
- Días 1-2: Preparación de datos y KPIs
- Días 3-4: Gráficos y filtros
- Día 5: Publicación e integración

### Semana 5-6: Chatbot Rasa
- Días 1-2: Configuración y 40 intents
- Días 3-4: FAQs y custom actions
- Días 5-6: Widget Angular
- Día 7: Testing y ajustes

### Semana 7: Limpieza
- Días 1-2: Limpieza de código y documentación

---

## MÉTRICAS DE ÉXITO

### UX Creación de Ticket
- ✅ Búsqueda responde en < 300ms
- ✅ 0 errores 422 en guardado
- ✅ Modales se muestran sin problemas de scroll

### Microservicio Catálogo
- ✅ API responde en < 200ms
- ✅ 100% de cobertura de endpoints
- ✅ Integrado en 2 módulos (dispositivo/ticket)

### Power BI
- ✅ 4 KPIs funcionando
- ✅ 6 gráficos renderizando correctamente
- ✅ Filtros interactivos operativos
- ✅ Embebido en módulo Reportes

### Chatbot Rasa
- ✅ 40 intents con > 80% precisión
- ✅ 10 FAQs conectadas a DB
- ✅ Widget funcional en Angular
- ✅ Tiempo de respuesta < 2s

### Limpieza de Código
- ✅ 0 comentarios obsoletos
- ✅ Docstrings en funciones complejas
- ✅ Código organizado y legible

---

## NOTAS IMPORTANTES

1. **Priorizar objetivos de alta prioridad** antes de avanzar a los de media/baja
2. **Testing continuo** durante el desarrollo
3. **Documentar cambios** en cada objetivo
4. **Commits frecuentes** con mensajes descriptivos
5. **Comunicar bloqueadores** inmediatamente

---

**Última actualización:** Enero 2025  
**Próxima revisión:** Al completar cada objetivo

