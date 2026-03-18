from __future__ import annotations
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'ingles-definitivo-maestro.md'
GUIDE = ROOT / 'guia_maestra.json'
QUEST = ROOT / 'preguntas.json'
SCHEMA = ROOT / 'schema.md'

TOP_SECTIONS = [
    'Collocations / Idioms / Fixed Expressions / False Friends',
    'Tiempos verbales y gramática',
    'Verbos irregulares y regulares policiales',
    'Vocabulario',
    'Linking Words',
    'Reading y Paráfrasis',
    'Situaciones funcionales',
    'Common Mistakes',
    'Explicación de términos',
    'Exámenes / sets / simulacros',
]

KEYWORDS = {
    'Reading y Paráfrasis': ['coletillas', 'reading', 'paráfrasis', 'murder mystery', 'bag theft', 'reading 1'],
    'Collocations / Idioms / Fixed Expressions / False Friends': ['collocation', 'idiom', 'fixed expression', 'false friends', 'friends', 'calcos'],
    'Tiempos verbales y gramática': ['tiempos verbales', 'past simple', 'present perfect', 'past perfect', 'grammar', 'futuros', 'relative clauses', 'formal / legal grammar'],
    'Verbos irregulares y regulares policiales': ['irregulares', 'regulares muy policiales'],
    'Vocabulario': ['vocabulario', 'nouns', 'verbs', 'adjectives', 'adverbs', 'bloque vocabulario útil'],
    'Linking Words': ['linking words', 'conectores', 'timeline conector', 'result (consecuencia)'],
    'Situaciones funcionales': ['situaciones funcionales', 'entrevista', 'cctv.', 'prevención / seguridad', 'infracciones'],
    'Common Mistakes': ['common mistakes', 'errores que más penalizan', 'errores más repetidos', 'calcos que suenan', 'errores funcionales'],
    'Explicación de términos': ['explicación de términos', 'pregunta de examen'],
    'Exámenes / sets / simulacros': ['set 01', 'set 02', 'set 03', 'canaria examen', 'local examen'],
}


def slug(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r'[^a-z0-9áéíóúüñ]+', '-', s)
    return s.strip('-') or 'item'


def normalize_heading(text: str) -> str:
    return re.sub(r'\s+', ' ', text.replace('#', '').strip())


def map_section(stack: list[str], block: str) -> str:
    hay = ' '.join(stack + [block]).lower()
    for sec, keys in KEYWORDS.items():
        if any(k in hay for k in keys):
            return sec
    return 'Reading y Paráfrasis'


def kind_for(stack: list[str], block: str) -> str:
    text = ' '.join(stack + [block]).lower()
    if any(key in text for key in ['## reading', 'reading —', 'murder mystery', 'bag theft on the promenade']) and len(block.split()) > 50:
        return 'reading_text'
    if 'respuesta correcta' in text or 'opciones:' in text:
        return 'exam_item'
    if 'incorrecto correcto' in text or 'error típico' in text or 'errores' in text:
        return 'mistake_note'
    if any(x in text for x in ['regla rápida', 'estructura', 'cuándo', 'uso (es)', 'trampas', 'pistas rápidas']):
        return 'grammar_rule'
    if any(x in text for x in ['model answer', 'respuesta modelo']):
        return 'model_answer'
    if any(x in text for x in ['coletilla', 'expresión', 'palabra', 'significado', 'sinónimos', 'fixed expression']):
        return 'reference'
    return 'mini_lesson'


def block_type(kind: str, block: str) -> str:
    text = block.lower()
    if kind == 'reading_text':
        return 'reading_comprehension'
    if kind == 'exam_item':
        if 'true/false' in text:
            return 'true_false'
        return 'multiple_choice'
    if 'matching' in text:
        return 'matching'
    if 'paráfrasis' in text or 'rephrase' in text:
        return 'paraphrase_write'
    if 'error' in text:
        return 'error_correction'
    return 'study_block'


def clean_block(lines: list[str]) -> str:
    out = []
    for line in lines:
        if line.strip().startswith('<!--'):
            continue
        out.append(line.rstrip())
    text = '\n'.join(out).strip()
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def parse_blocks(lines: list[str]):
    blocks = []
    stack: list[tuple[int,str,int]] = []
    buf: list[str] = []
    start_line = 1

    def flush(end_line: int):
        nonlocal buf, start_line
        text = clean_block(buf)
        if text:
            headings = [h for _, h, _ in stack]
            blocks.append({
                'headings': headings.copy(),
                'content': text,
                'line_start': start_line,
                'line_end': end_line,
            })
        buf = []
        start_line = end_line + 1

    for idx, line in enumerate(lines, 1):
        if re.match(r'^#{1,6} ', line):
            flush(idx - 1)
            level = len(line) - len(line.lstrip('#'))
            heading = normalize_heading(line)
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, heading, idx))
            start_line = idx
        else:
            buf.append(line)
    flush(len(lines))
    return blocks


def extract_questions_from_bullets(lines: list[str]):
    questions = []
    current = None
    current_section = None
    for idx, line in enumerate(lines, 1):
        low = line.lower().strip()
        if line.startswith('#'):
            current_section = normalize_heading(line)
        if low.startswith('*'):
            text = line.lstrip('*').strip()
            if not text:
                continue
            sec = map_section([current_section or ''], text)
            qid = f"q-{slug(sec)}-{idx}"
            questions.append({
                'id': qid,
                'section': sec,
                'subsection': current_section or sec,
                'kind': 'question',
                'type': 'translation_choice' if sec != 'Verbos irregulares y regulares policiales' else 'fill_in_the_blank',
                'title': f'Práctica derivada: {text.split()[0]}',
                'prompt': f"Usa este elemento del documento en contexto o identifica su significado: {text}",
                'content_es': text,
                'content_en': text,
                'answer': text.split(' ')[0],
                'acceptable_answers': [text.split(' ')[0]],
                'model_answer': f"Example: {text.split(' ')[0]} can be used correctly in a police/B1 context.",
                'bad_answers': [],
                'explanation_es': 'Ejercicio derivado automáticamente a partir de un elemento explícito del documento maestro. Se conserva el elemento original y se invita a usarlo o reconocerlo en contexto.',
                'examples': [text],
                'mistakes': [],
                'difficulty': 'intermediate',
                'tags': [slug(sec), 'derived-from-master'],
                'source_block': f'ingles-definitivo-maestro.md:{idx}',
                'original_phrase': text,
                'corrected_phrase': text,
            })
    return questions


def extract_exam_items(text: str):
    items = []
    set_pattern = re.compile(r'## (Set 0[123].*?)(?=\n## |\Z)', re.S)
    for m in set_pattern.finditer(text):
        title = m.group(1).strip()
        body = m.group(0)
        q_matches = list(re.finditer(r'(?:^|\n)(?:-\s*)?(\d+)\)\s*(.*?)(?=(?:\n(?:-\s*)?\d+\)|\Z))', body, re.S))
        for qm in q_matches:
            num = qm.group(1)
            chunk = qm.group(2).strip()
            answer = ''
            am = re.search(r'Respuesta\s+correcta:\s*(.+?)(?:\n|$)', chunk, re.I)
            if not am:
                am = re.search(r'Respuesta correcta:\s*(.+?)(?:\n|$)', chunk, re.I)
            if am:
                answer = am.group(1).strip()
            items.append({
                'id': f"exam-{slug(title)}-{num}",
                'section': 'Exámenes / sets / simulacros',
                'subsection': title,
                'kind': 'exam_item',
                'type': 'multiple_choice',
                'title': f'{title} · Pregunta {num}',
                'prompt': chunk.split('###')[0].strip(),
                'content_es': chunk,
                'content_en': '',
                'choices': [],
                'answer': answer,
                'acceptable_answers': [answer] if answer else [],
                'model_answer': '',
                'bad_answers': [],
                'explanation_es': 'Ítem conservado del simulacro del documento maestro. El bloque completo incluye opciones y explicación por opción dentro del contenido asociado.',
                'examples': [],
                'mistakes': [],
                'difficulty': 'intermediate',
                'tags': ['exam', slug(title)],
                'source_block': 'ingles-definitivo-maestro.md',
            })
    return items


def extract_reading_questions(lines: list[str]):
    items = []
    current_reading = None
    for idx, line in enumerate(lines, 1):
        if line.startswith('## READING'):
            current_reading = normalize_heading(line)
        if re.match(r'^# \d+\.', line) and current_reading:
            prompt = normalize_heading(line)
            items.append({
                'id': f'reading-q-{idx}',
                'section': 'Reading y Paráfrasis',
                'subsection': current_reading,
                'kind': 'question',
                'type': 'reading_comprehension',
                'title': prompt,
                'prompt': prompt,
                'content_es': '',
                'content_en': '',
                'choices': [],
                'answer': '',
                'acceptable_answers': [],
                'model_answer': '',
                'bad_answers': [],
                'explanation_es': 'Pregunta de reading conservada del documento. Consulta el bloque del reading y la explicación/paráfrasis asociada en la guía maestra.',
                'examples': [],
                'mistakes': [],
                'difficulty': 'intermediate',
                'tags': ['reading', slug(current_reading)],
                'source_block': f'ingles-definitivo-maestro.md:{idx}',
                'reading_id': slug(current_reading),
            })
    return items


def main():
    raw = SRC.read_text(encoding='utf-8')
    lines = raw.splitlines()
    blocks = parse_blocks(lines)

    guide_items = []
    for i, block in enumerate(blocks, 1):
        headings = block['headings'] or ['Base']
        section = map_section(headings, block['content'])
        kind = kind_for(headings, block['content'])
        item = {
            'id': f"guide-{i:04d}-{slug(headings[-1])}",
            'section': section,
            'subsection': headings[-1],
            'kind': kind,
            'type': block_type(kind, block['content']),
            'title': headings[-1],
            'prompt': headings[-1],
            'content_es': block['content'],
            'content_en': block['content'] if section in ['Reading y Paráfrasis', 'Situaciones funcionales', 'Explicación de términos'] else '',
            'choices': [],
            'answer': '',
            'acceptable_answers': [],
            'model_answer': '',
            'bad_answers': [],
            'explanation_es': f"Bloque conservado del documento maestro entre las líneas {block['line_start']}-{block['line_end']}.",
            'examples': [],
            'mistakes': [],
            'difficulty': 'intermediate',
            'tags': [slug(section), slug(headings[-1])],
            'source_block': f"ingles-definitivo-maestro.md:{block['line_start']}-{block['line_end']}",
            'source_lines': {'start': block['line_start'], 'end': block['line_end']},
        }
        guide_items.append(item)

    question_items = []
    question_items.extend(extract_questions_from_bullets(lines))
    question_items.extend(extract_exam_items(raw))
    question_items.extend(extract_reading_questions(lines))

    guide_payload = {
        'source': 'ingles-definitivo-maestro.md',
        'top_sections': TOP_SECTIONS,
        'items': guide_items,
    }
    question_payload = {
        'source': 'ingles-definitivo-maestro.md',
        'top_sections': TOP_SECTIONS,
        'items': question_items,
    }

    GUIDE.write_text(json.dumps(guide_payload, ensure_ascii=False, indent=2), encoding='utf-8')
    QUEST.write_text(json.dumps(question_payload, ensure_ascii=False, indent=2), encoding='utf-8')

    SCHEMA.write_text('''# Esquema de datos\n\n- `guia_maestra.json`: conserva **todo** el contenido del documento maestro en bloques estructurados con `id`, `section`, `subsection`, `kind`, `type`, `content_es`, `source_block` y metadatos.\n- `preguntas.json`: banco de práctica derivado y conservado a partir de elementos explícitos del documento (`*items`, preguntas de reading y sets de examen).\n- Ambos ficheros están pensados para GitHub Pages y carga vía `fetch`.\n''', encoding='utf-8')

    print(f'guide_items={len(guide_items)}')
    print(f'question_items={len(question_items)}')

if __name__ == '__main__':
    main()
