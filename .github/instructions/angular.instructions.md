---
name: Angular de ProGesTec
description: "Usar al editar Angular, TypeScript, HTML o CSS del frontend de ProGesTec."
applyTo: "progestec-front/**/*.ts, progestec-front/**/*.html, progestec-front/**/*.css"
---

# Reglas de Angular

- Conserva los componentes standalone de Angular 20 y la compatibilidad con SSR.
- Conserva la carga lazy por rutas y los limites existentes entre core, features y shared.
- Protege las APIs exclusivas del navegador con las comprobaciones de plataforma existentes.
- Mantén el acceso HTTP en los servicios de core y conserva los modelos tipados.
- Prefiere observables o signals segun el codigo cercano; no introduzcas una libreria de estado sin necesidad.
- Usa etiquetas accesibles, estados de foco, operacion con teclado y estados explicitos de carga, error y vacio.
- Agrega o actualiza una prueba Jasmine enfocada cuando cambie el comportamiento.
- Ejecuta las pruebas unitarias y el build de produccion del frontend despues de editar.
