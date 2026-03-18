# Esquema de datos

- `guia_maestra.json`: conserva **todo** el contenido del documento maestro en bloques estructurados con `id`, `section`, `subsection`, `kind`, `type`, `content_es`, `source_block` y metadatos.
- `preguntas.json`: banco ampliado de preguntas generado desde el documento maestro (definiciones, gramática, readings y sets de examen).
- Ambos ficheros están pensados para GitHub Pages y carga vía `fetch`.
