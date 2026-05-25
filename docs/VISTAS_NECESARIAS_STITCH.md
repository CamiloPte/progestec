# VISTAS NECESARIAS DE STITCH
## Lista de pantallas y componentes para los próximos pasos

---

## ✅ VISTAS YA IMPLEMENTADAS (No necesitas generarlas)

1. **Dashboard** - Ya implementado
2. **Listado de Tickets** - Ya implementado
3. **Detalle de Ticket** - ✅ **Recién ajustado según Stitch**
4. **Crear Ticket** - Ya implementado (necesita mejoras de UX)

---

## 🎯 VISTAS PRIORITARIAS PARA PASO 1 (Mejoras UX Creación de Ticket)

### 1. Modal de Búsqueda de Cliente Mejorado
**Descripción:** Modal o dropdown mejorado para búsqueda de clientes con:
- Búsqueda en vivo mientras se escribe
- Resultados con información completa (nombre, teléfono, email, ID)
- Highlight de coincidencias
- Indicador de carga
- Diseño moderno y responsivo (consecuente con el diseño que llevamos implementado)

**Elementos clave:**
- Input de búsqueda con debounce visual
- Lista de resultados con cards
- Información visible: nombre, teléfono, email, tipo/número ID
- Botón "Seleccionar" en cada resultado

---

### 2. Modal de Búsqueda de Dispositivo Mejorado
**Descripción:** Similar al de cliente pero para dispositivos:
- Búsqueda por serial, IMEI, marca, modelo
- Resultados con información del dispositivo
- Filtrado en tiempo real
- Diseño consistente con búsqueda de cliente

**Elementos clave:**
- Input de búsqueda
- Lista de resultados con información completa
- Mostrar: marca, modelo, tipo, serial/IMEI
- Botón "Seleccionar"

---

### 3. Overlay de Carga/Procesamiento
**Descripción:** Overlay mejorado para estados de carga:
- Animación suave
- Mensajes contextuales
- No bloquea completamente la interacción si es posible

---

## 🎯 VISTAS PARA PASO 2 (Microservicio Catálogo)

### 4. Selector de Fabricante/Modelo/Variante
**Descripción:** Componente de selección en cascada para el catálogo:
- Select de Fabricante (dropdown)
- Select de Modelo (se habilita después de seleccionar fabricante)
- Select de Variante (se habilita después de seleccionar modelo)
- Indicadores de carga mientras se cargan opciones
- Diseño integrado en el modal de creación de dispositivo

**Elementos clave:**
- 3 selects en cascada
- Estados disabled/enabled según selección
- Loading states
- Auto-completado de campos (marca, modelo, tipo)

---

## 🎯 VISTAS PARA PASO 3 (Power BI - Reportes)

### 5. Página de Reportes
**Descripción:** Página principal del módulo de reportes:
- Header con título "Reportes"
- Área para embebido de Power BI
- Filtros interactivos (si aplica)
- Diseño limpio y profesional

**Elementos clave:**
- Contenedor para iframe de Power BI
- Filtros de fecha, técnico, estado (opcional)
- Botones de exportación (opcional)

---

## 🎯 VISTAS PARA PASO 4 (Chatbot Rasa)

### 6. Widget de Chatbot
**Descripción:** Widget flotante de chat:
- Botón flotante para abrir/cerrar
- Ventana de chat con historial
- Input para escribir mensajes
- Indicadores de "escribiendo..."
- Diseño moderno y discreto

**Elementos clave:**
- Botón flotante (esquina inferior derecha)
- Ventana de chat expandible
- Burbujas de mensajes (usuario/robot)
- Input de texto con botón enviar
- Scroll automático en historial

---

## 🎯 VISTAS ADICIONALES (Futuras)

### 7. Modal de Cambio de Estado (Mejorado)
**Descripción:** Si quieres mejorar el modal actual:
- Diseño más moderno
- Validaciones visuales
- Preview del cambio

### 8. Modal de Actualización de Diagnóstico (Mejorado)
**Descripción:** Similar al anterior pero para diagnóstico

### 9. Modal de Actualización de Presupuesto (Mejorado)
**Descripción:** Similar pero para presupuesto

### 10. Vista de Listado de Dispositivos
**Descripción:** Página para gestionar dispositivos (módulo DEVICES):
- Tabla con dispositivos
- Filtros
- Acciones (editar, ver, eliminar)

### 11. Vista de Gestión de Usuarios
**Descripción:** Página para gestionar usuarios (módulo USERS):
- Tabla con usuarios
- Filtros por rol
- Acciones CRUD

### 12. Vista de Finanzas
**Descripción:** Página del módulo FINANCE:
- Dashboard financiero
- Ingresos/Egresos
- Facturación
- Reportes

---

## 📋 PRIORIDAD DE GENERACIÓN

### 🔴 Alta Prioridad (Paso 1 - Inmediato)
1. ✅ **Modal de Búsqueda de Cliente Mejorado**
2. ✅ **Modal de Búsqueda de Dispositivo Mejorado**
3. ✅ **Overlay de Carga Mejorado**

### 🟡 Media Prioridad (Paso 2 - Próxima semana)
4. ✅ **Selector de Fabricante/Modelo/Variante**

### 🟢 Baja Prioridad (Pasos 3-4 - Después)
5. ✅ **Página de Reportes**
6. ✅ **Widget de Chatbot**

---

## 📝 NOTAS PARA STITCH

- **Consistencia:** Mantén el mismo estilo visual que ya tienes (colores, tipografía, espaciado)
- **Responsive:** Todas las vistas deben funcionar en móvil y desktop
- **Accesibilidad:** Contraste adecuado, labels claros, estados focus visibles
- **Estados:** Incluye estados de hover, active, disabled, loading
- **Iconos:** Usa iconos consistentes (puedes usar emojis o iconos de librería)

---

## 🎨 ESPECIFICACIONES TÉCNICAS

### Colores del Sistema (ya definidos)
- **Azul (Recibido):** `#1f6feb`
- **Cian (Diagnóstico):** `#0f8fa6`
- **Amarillo (Aprobación):** `#f59e0b`
- **Naranja (Reparación):** `#f5a524`
- **Verde (Cerrado):** `#2e7d32` / `#22c55e` / `#16a34a`

### Tipografía
- Títulos: Bold, 1.1rem - 2rem
- Texto normal: Regular, 0.95rem
- Labels: Semibold, 0.85rem, uppercase, letter-spacing

### Espaciado
- Cards: padding 1.5rem, border-radius 16px
- Gaps: 1rem - 1.5rem entre elementos
- Inputs: padding 0.75rem, border-radius 12px

---

**Última actualización:** Enero 2025  
**Próxima revisión:** Al completar cada paso

