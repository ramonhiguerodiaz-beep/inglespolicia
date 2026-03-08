# Auditoría rápida y tareas propuestas

## 1) Tarea de corrección tipográfica
**Hallazgo:** En las etiquetas de tipo de pregunta, `idiom` se muestra como `Idiom`, mientras que en el resto de la UI y del banco de preguntas se usa el plural (`Idioms`) y nomenclatura equivalente en plural para bloques.

**Propuesta de tarea:** Normalizar la etiqueta a `Idioms` (o `Modismos`, si se decide unificar toda la interfaz al español) en el diccionario `TLAB`.

**Criterio de aceptación:** Al renderizar preguntas de tipo `idiom`, la píldora muestra la forma final acordada (sin inconsistencias de singular/plural).

---

## 2) Tarea para solucionar un fallo funcional
**Hallazgo:** En `rRes()`, el porcentaje final se calcula como `Math.round((okN/t)*100)` sin proteger el caso `t === 0`. Si en el futuro el banco queda vacío, un filtro deja 0 preguntas, o hay una carga parcial de datos, el resultado puede ser `NaN`.

**Propuesta de tarea:** Añadir guardas para evitar división por cero (`t ? ... : 0`) y definir comportamiento cuando no hay preguntas (mensaje de estado + CTA para recargar/restablecer).

**Criterio de aceptación:** Con `Q=[]` o colección vacía, la aplicación no rompe y muestra un estado controlado con porcentaje `0%`.

---

## 3) Tarea de comentario/documentación
**Hallazgo:** El comentario introductorio del bloque `SIMULACRO 023 APOLOCAN` contiene una descripción narrativa que no funciona como documentación técnica del bloque (fuente, alcance, criterios, estructura esperada de ítems), lo que dificulta mantenimiento y onboarding.

**Propuesta de tarea:** Sustituir/expandir el comentario por documentación técnica breve del bloque:
- objetivo del bloque,
- formato de preguntas,
- campos obligatorios por ítem,
- convención de etiquetado (`cat`, `type`, `ctx`, `exp`).

**Criterio de aceptación:** Cualquier persona puede añadir una pregunta nueva del simulacro sin inferir estructura leyendo múltiples ejemplos.

---

## 4) Tarea para mejorar pruebas
**Hallazgo:** No hay pruebas automatizadas para la lógica central (`getQ`, `pick`, `rRes`, conteos por categoría, progreso).

**Propuesta de tarea:** Crear una suite mínima (p. ej. con Vitest/Jest + jsdom) para cubrir:
- barajado/filtrado no destructivo,
- actualización de `okN/errN` y `cSt` en `pick`,
- cálculo de porcentaje y estado de aprobado/suspenso en `rRes`,
- caso borde con 0 preguntas.

**Criterio de aceptación:** Suite ejecutable en CI con cobertura básica sobre funciones de estado y render principal.
