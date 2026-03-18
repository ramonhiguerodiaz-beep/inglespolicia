from __future__ import annotations

import json
import re
from collections import defaultdict
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

SPANISH_HINTS = {
    'al', 'alguien', 'algo', 'antes', 'bajo', 'cámara', 'carterismo', 'caso', 'cerca', 'citación', 'claro', 'comisaría',
    'con', 'condena', 'culpable', 'custodia', 'delito', 'detener', 'detenido', 'dinero', 'documentos', 'evidencia',
    'expresión', 'falso', 'grave', 'hecho', 'huellas', 'huir', 'ilegal', 'impune', 'infracción', 'interrogar', 'juicio',
    'ley', 'menor', 'multa', 'oficialmente', 'pistas', 'prisión', 'prueba', 'pruebas', 'real', 'rehén', 'resolver',
    'retener', 'retirar', 'robar', 'robo', 'seguridad', 'sentencia', 'seguir', 'señal', 'sospechoso', 'suceso',
    'testigo', 'tienda', 'vigilante', 'verdadero', 'violencia', 'culpa', 'acusado', 'agentes', 'escena', 'crimen',
    'detención', 'registrar', 'rescate', 'pregunta', 'respuesta', 'significado', 'significa', 'explica', 'explicar',
    'pasado', 'presente', 'hábito', 'duración', 'momento', 'lugar', 'mientras', 'aunque', 'porque', 'resultado',
}

ENGLISH_ALLOWLIST = {
    'a', 'an', 'and', 'arrest', 'assistant', 'away', 'bail', 'bank', 'be', 'been', 'break', 'broken', 'by', 'camera',
    'case', 'caught', 'charge', 'clue', 'crime', 'criminal', 'cross', 'custody', 'evidence', 'false', 'file', 'follow',
    'for', 'gather', 'get', 'guard', 'handed', 'have', 'identity', 'incident', 'into', 'jail', 'law', 'lead', 'manager',
    'murder', 'offence', 'officer', 'officers', 'on', 'out', 'piece', 'place', 'police', 'proof', 'question', 'red',
    'report', 'scene', 'search', 'security', 'someone', 'station', 'suspect', 'take', 'the', 'their', 'under', 'with',
    'witness', 'word', 'words', 'work', 'working', 'follow', 'crack', 'break', 'actual', 'crime', 'felony', 'misdemeanor',
    'summons', 'book', 'press', 'charges', 'footage', 'shopping', 'center', 'store', 'pickpocketing', 'mugging', 'burglary',
    'sentence', 'penalty', 'ruling', 'security', 'camera', 'cctv', 'crime', 'scene', 'police', 'station', 'assistant',
}


def slug(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r'[^a-z0-9áéíóúüñ]+', '-', value)
    return value.strip('-') or 'item'


def normalize_heading(text: str) -> str:
    return re.sub(r'\s+', ' ', text.replace('#', '').strip())


def map_section(stack: list[str], block: str) -> str:
    hay = ' '.join(stack + [block]).lower()
    for section, keys in KEYWORDS.items():
        if any(key in hay for key in keys):
            return section
    return 'Reading y Paráfrasis'


def kind_for(stack: list[str], block: str) -> str:
    text = ' '.join(stack + [block]).lower()
    if any(key in text for key in ['## reading', 'reading —', 'murder mystery', 'bag theft on the promenade']) and len(block.split()) > 50:
        return 'reading_text'
    if 'respuesta correcta' in text or 'opciones:' in text:
        return 'exam_item'
    if 'incorrecto correcto' in text or 'error típico' in text or 'errores' in text:
        return 'mistake_note'
    if any(value in text for value in ['regla rápida', 'estructura', 'cuándo', 'uso (es)', 'trampas', 'pistas rápidas']):
        return 'grammar_rule'
    if any(value in text for value in ['model answer', 'respuesta modelo']):
        return 'model_answer'
    if any(value in text for value in ['coletilla', 'expresión', 'palabra', 'significado', 'sinónimos', 'fixed expression']):
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
    cleaned = []
    for line in lines:
        if line.strip().startswith('<!--'):
            continue
        cleaned.append(line.rstrip())
    text = '\n'.join(cleaned).strip()
    return re.sub(r'\n{3,}', '\n\n', text).strip()


def parse_blocks(lines: list[str]):
    blocks = []
    stack: list[tuple[int, str, int]] = []
    buffer: list[str] = []
    start_line = 1

    def flush(end_line: int):
        nonlocal buffer, start_line
        text = clean_block(buffer)
        if text:
            blocks.append({
                'headings': [heading for _, heading, _ in stack],
                'content': text,
                'line_start': start_line,
                'line_end': end_line,
            })
        buffer = []
        start_line = end_line + 1

    for index, line in enumerate(lines, 1):
        if re.match(r'^#{1,6} ', line):
            flush(index - 1)
            level = len(line) - len(line.lstrip('#'))
            heading = normalize_heading(line)
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, heading, index))
            start_line = index
        else:
            buffer.append(line)
    flush(len(lines))
    return blocks


def compact_text(text: str) -> str:
    return re.sub(r'\s+', ' ', str(text or '')).strip()


def make_choice_objects(options: list[str]) -> list[dict[str, str]]:
    letters = ['a', 'b', 'c', 'd']
    return [{'key': letters[index], 'label': option} for index, option in enumerate(options[:4])]


def build_question_item(*, item_id: str, section: str, subsection: str, qtype: str, title: str, prompt: str,
                        choices: list[dict[str, str]], answer_index: int, explanation: str, source_block: str,
                        difficulty: str = 'intermediate', tags: list[str] | None = None, reading_id: str | None = None):
    answer = f"{chr(97 + answer_index)}) {choices[answer_index]['label']}" if choices else ''
    return {
        'id': item_id,
        'section': section,
        'subsection': subsection,
        'kind': 'question',
        'type': qtype,
        'title': title,
        'prompt': prompt,
        'content_es': prompt,
        'content_en': '',
        'choices': choices,
        'answer': answer,
        'acceptable_answers': [answer, choices[answer_index]['key']] if choices else [],
        'model_answer': '',
        'bad_answers': [],
        'explanation_es': explanation,
        'examples': [],
        'mistakes': [],
        'difficulty': difficulty,
        'tags': tags or [],
        'source_block': source_block,
        **({'reading_id': reading_id} if reading_id else {}),
    }


def looks_spanish_token(token: str) -> bool:
    cleaned = token.strip('.,;:()[]¿?¡!*/').lower()
    if not cleaned:
        return False
    if any(char in cleaned for char in 'áéíóúñü'):
        return True
    if cleaned in SPANISH_HINTS:
        return True
    if cleaned in ENGLISH_ALLOWLIST:
        return False
    if cleaned.endswith(('ción', 'sión', 'mente', 'dad', 'tad', 'ario', 'aria', 'ez', 'eza', 'ado', 'ada', 'idos', 'idas', 'ismo', 'ista')):
        return True
    return False


def split_term_definition(text: str) -> tuple[str, str]:
    cleaned = compact_text(re.sub(r'^[*\-]\s*', '', text))
    cleaned = re.split(r'\b(?:What this|It means|This expression|Model answer|Example:|Error típico|Clave:|Correcta:|Incorrecta:)\b', cleaned)[0].strip()
    cleaned = re.split(r'\s[*][A-Za-z]', cleaned)[0].strip()
    tokens = cleaned.split()
    if len(tokens) < 2:
        return cleaned, ''

    boundary = None
    for index in range(1, min(len(tokens), 8)):
        if looks_spanish_token(tokens[index]):
            boundary = index
            break
    if boundary is None:
        boundary = 1

    term = compact_text(' '.join(tokens[:boundary]))
    definition = compact_text(' '.join(tokens[boundary:]))
    return term, definition


def extract_definition_questions(lines: list[str]) -> list[dict]:
    parsed_entries = []
    current_headings: list[str] = []

    for line_number, raw_line in enumerate(lines, 1):
        line = raw_line.rstrip()
        if re.match(r'^#{1,6} ', line):
            heading = normalize_heading(line)
            level = len(line) - len(line.lstrip('#'))
            current_headings = current_headings[:max(level - 1, 0)]
            current_headings.append(heading)
            continue

        if not line.lstrip().startswith('*'):
            continue

        section = map_section(current_headings, line)
        if section == 'Exámenes / sets / simulacros':
            continue

        term, definition = split_term_definition(line)
        if not term or not definition:
            continue

        subsection = current_headings[-1] if current_headings else section
        parsed_entries.append({
            'term': term,
            'definition': definition,
            'section': section,
            'subsection': subsection,
            'line_number': line_number,
            'raw': compact_text(line),
        })

    by_bucket: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for entry in parsed_entries:
        by_bucket[(entry['section'], entry['subsection'])].append(entry)

    questions = []
    for (section, subsection), entries in by_bucket.items():
        for index, entry in enumerate(entries):
            distractor_pool = [candidate['term'] for candidate in entries if candidate['term'] != entry['term']]
            if len(distractor_pool) < 3:
                distractor_pool.extend([
                    candidate['term']
                    for candidate in parsed_entries
                    if candidate['section'] == section and candidate['term'] != entry['term'] and candidate['term'] not in distractor_pool
                ])
            distractors = distractor_pool[:3]
            if len(distractors) < 3:
                continue

            options = [entry['term'], *distractors]
            choices = make_choice_objects(options)
            prompt = f"¿Qué expresión o término encaja mejor con esta idea? {entry['definition']}"
            questions.append(build_question_item(
                item_id=f"def-{slug(section)}-{slug(subsection)}-{index + 1}",
                section=section,
                subsection=subsection,
                qtype='multiple_choice',
                title=f'{subsection} · definición',
                prompt=prompt,
                choices=choices,
                answer_index=0,
                explanation=f"Elemento derivado directamente del documento maestro: {entry['raw']}",
                source_block=f'ingles-definitivo-maestro.md:{entry["line_number"]}',
                tags=[slug(section), 'derived-definition'],
            ))
    return questions


def extract_grammar_examples(lines: list[str]) -> list[dict]:
    questions = []
    current_headings: list[str] = []

    for line_number, raw_line in enumerate(lines, 1):
        line = compact_text(raw_line)
        if re.match(r'^#{1,6} ', raw_line):
            heading = normalize_heading(raw_line)
            level = len(raw_line) - len(raw_line.lstrip('#'))
            current_headings = current_headings[:max(level - 1, 0)]
            current_headings.append(heading)
            continue

        match = re.search(r'A:\s*(.+?)\s+N:\s*(.+?)\s+Q:\s*(.+)', line)
        if not match:
            continue

        affirmative, negative, interrogative = [compact_text(group) for group in match.groups()]
        section = map_section(current_headings, line)
        subsection = current_headings[-1] if current_headings else section
        title = subsection if subsection != section else 'Gramática'

        prompts = [
            ('affirmative', '¿Cuál es el ejemplo afirmativo correcto según el documento?', affirmative, [affirmative, negative, interrogative]),
            ('negative', '¿Cuál es el ejemplo negativo correcto según el documento?', negative, [negative, affirmative, interrogative]),
            ('question', '¿Cuál es la pregunta correcta según el documento?', interrogative, [interrogative, affirmative, negative]),
        ]

        for offset, (label, prompt, answer, options) in enumerate(prompts, 1):
            questions.append(build_question_item(
                item_id=f"grammar-{slug(subsection)}-{line_number}-{offset}",
                section='Tiempos verbales y gramática',
                subsection=subsection,
                qtype='grammar_choice',
                title=f'{title} · {label}',
                prompt=prompt,
                choices=make_choice_objects(options),
                answer_index=0,
                explanation=f"Ejemplo A/N/Q conservado del documento maestro. Línea original: {line}",
                source_block=f'ingles-definitivo-maestro.md:{line_number}',
                tags=['grammar', slug(subsection), label],
            ))
    return questions


def extract_exam_items(text: str) -> list[dict]:
    items = []
    set_pattern = re.compile(r'## (Set 0[123].*?)(?=\n## |\Z)', re.S)
    for match in set_pattern.finditer(text):
        title = compact_text(match.group(1))
        body = match.group(0)
        question_matches = list(re.finditer(r'(?:^|\n)(?:-\s*)?(\d+)\)\s*(.*?)(?=(?:\n(?:-\s*)?\d+\)|\Z))', body, re.S))
        for question_match in question_matches:
            number = question_match.group(1)
            chunk = compact_text(question_match.group(2))
            answer = ''
            answer_match = re.search(r'Respuesta\s+correcta:\s*(.+?)(?:\s+Explicación|\n|$)', chunk, re.I)
            if answer_match:
                answer = compact_text(answer_match.group(1))
            items.append({
                'id': f"exam-{slug(title)}-{number}",
                'section': 'Exámenes / sets / simulacros',
                'subsection': title,
                'kind': 'exam_item',
                'type': 'multiple_choice',
                'title': f'{title} · Pregunta {number}',
                'prompt': chunk,
                'content_es': chunk,
                'content_en': '',
                'choices': [],
                'answer': answer,
                'acceptable_answers': [answer] if answer else [],
                'model_answer': '',
                'bad_answers': [],
                'explanation_es': 'Ítem conservado del simulacro del documento maestro. El bloque completo incluye opciones y explicación por opción en el contenido.',
                'examples': [],
                'mistakes': [],
                'difficulty': 'intermediate',
                'tags': ['exam', slug(title)],
                'source_block': 'ingles-definitivo-maestro.md',
            })
    return items


def extract_reading_questions(lines: list[str]) -> list[dict]:
    items = []
    current_reading = None
    for line_number, line in enumerate(lines, 1):
        if line.startswith('## READING'):
            current_reading = normalize_heading(line)
        if re.match(r'^# \d+\.', line) and current_reading:
            prompt = normalize_heading(line)
            items.append({
                'id': f'reading-q-{line_number}',
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
                'explanation_es': 'Pregunta de reading conservada del documento. Consulta el bloque del reading y la paráfrasis asociada en la guía maestra.',
                'examples': [],
                'mistakes': [],
                'difficulty': 'intermediate',
                'tags': ['reading', slug(current_reading)],
                'source_block': f'ingles-definitivo-maestro.md:{line_number}',
                'reading_id': slug(current_reading),
            })
    return items


def main() -> None:
    raw = SRC.read_text(encoding='utf-8')
    lines = raw.splitlines()
    blocks = parse_blocks(lines)

    guide_items = []
    for index, block in enumerate(blocks, 1):
        headings = block['headings'] or ['Base']
        section = map_section(headings, block['content'])
        kind = kind_for(headings, block['content'])
        guide_items.append({
            'id': f"guide-{index:04d}-{slug(headings[-1])}",
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
        })

    question_items = []
    question_items.extend(extract_definition_questions(lines))
    question_items.extend(extract_grammar_examples(lines))
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
    SCHEMA.write_text(
        '# Esquema de datos\n\n'
        '- `guia_maestra.json`: conserva **todo** el contenido del documento maestro en bloques estructurados con `id`, `section`, `subsection`, `kind`, `type`, `content_es`, `source_block` y metadatos.\n'
        '- `preguntas.json`: banco ampliado de preguntas generado desde el documento maestro (definiciones, gramática, readings y sets de examen).\n'
        '- Ambos ficheros están pensados para GitHub Pages y carga vía `fetch`.\n',
        encoding='utf-8',
    )

    print(f'guide_items={len(guide_items)}')
    print(f'question_items={len(question_items)}')


if __name__ == '__main__':
    main()
