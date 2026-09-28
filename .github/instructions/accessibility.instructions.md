---
name: Accesibilidad de ProGesTec
description: "Usar al editar interfaz web, formularios, dialogos, navegacion, tablas o layouts responsivos."
applyTo: "progestec-front/**/*.html, progestec-front/**/*.css, progestec-front/**/*.ts"
---

# Reglas de accesibilidad

- Usa landmarks semanticos, encabezados y controles nativos antes que ARIA.
- Cada control de formulario necesita una etiqueta visible o programatica y un error comprensible.
- Los dialogos deben gestionar el foco, admitir Escape cuando corresponda y devolver el foco al disparador.
- Todas las acciones deben funcionar con teclado y mostrar el foco de forma visible.
- No comuniques estados usando solamente el color.
- Respeta las preferencias de movimiento reducido y conserva objetivos tactiles usables en pantallas pequeñas.
- Revisa estados vacios, de carga, error, deshabilitado y exito durante las revisiones de interfaz.
