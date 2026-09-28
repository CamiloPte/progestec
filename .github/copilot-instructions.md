# Instrucciones de Copilot para ProGesTec

- Trata este repositorio como un producto orientado a produccion, no como un prototipo academico.
- Lee el codigo, las pruebas y la documentacion canonica relevante antes de editar.
- Mantén los cambios pequeños, explicitos y limitados al area solicitada.
- Conserva los limites del monorepo: FastAPI/MySQL, Angular SSR y catalogo Express/PostgreSQL.
- No introduzcas AEM, HTL, React, Vue, Tailwind ni frameworks no relacionados.
- Flujo backend: routes -> services -> crud -> models/schemas. La logica de negocio vive en services.
- El frontend usa componentes standalone de Angular 20, rutas lazy, TypeScript y RxJS.
- Los contratos backend/frontend deben revisarse juntos cuando cambie una API.
- CORS es deliberadamente permisivo en desarrollo local. No lo cambies en tareas no relacionadas.
- Nunca expongas secretos, tokens, uploads, dumps de bases de datos ni datos reales de clientes.
- No ejecutes migraciones destructivas, resets, borrados ni acciones productivas sin confirmacion explicita.
- Despues de editar, ejecuta la prueba, lint o build mas especifico antes de ampliar el alcance.
- Actualiza la documentacion canonica cuando cambie el comportamiento, la arquitectura, la operacion o el roadmap.
- Mantén los comentarios de codigo breves y directos; agregalos solo para explicar decisiones o contexto no obvio.
- No narres linea por linea, no repitas lo que el codigo ya expresa y no agregues bloques extensos de comentarios.
- Usa español en los textos dirigidos al usuario y ASCII en los archivos fuente salvo que el archivo requiera otra codificacion.
