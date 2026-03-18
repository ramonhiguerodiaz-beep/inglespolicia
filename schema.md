# Esquema de datos

- `guia_maestra.json`: conserva **todo** el contenido del documento maestro en bloques estructurados con `id`, `section`, `subsection`, `kind`, `type`, `content_es`, `source_block` y metadatos.
- `preguntas.json`: banco de práctica derivado y conservado a partir de elementos explícitos del documento (`*items`, preguntas de reading y sets de examen).
- Ambos ficheros están pensados para GitHub Pages y carga vía `fetch`.
