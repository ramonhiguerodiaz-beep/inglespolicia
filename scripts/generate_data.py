from __future__ import annotations

import json
import random
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

CURATED_COLLOCATIONS = [
    ('make an arrest', 'efectuar una detención', 'do an arrest', 430),
    ('place someone under arrest', 'poner a alguien bajo arresto', 'make someone under arrest', 431),
    ('commit a crime', 'cometer un delito', 'make a crime', 433),
    ('carry out an investigation', 'llevar a cabo una investigación', 'do an investigation', 434),
    ('launch an inquiry', 'iniciar una investigación formal', 'make an inquiry', 437),
    ('gather evidence', 'recopilar pruebas', 'gather proofs / collect evidences', 439),
    ('question a suspect', 'interrogar a un sospechoso', 'question to a suspect', 440),
    ('file a report', 'redactar o presentar un informe', 'make a report', 441),
    ('press charges', 'presentar cargos', 'put charges', 442),
    ('open / close a case', 'abrir o cerrar un caso', 'open the crime', 443),
    ('patrol an area', 'patrullar una zona', 'patrol in the area', 444),
    ('respond to an incident', 'responder a un incidente', 'respond an incident', 445),
    ('use reasonable force', 'usar fuerza proporcionada', 'use reasonable forces', 447),
    ('face charges', 'enfrentarse a cargos', 'face to charges', 453),
    ('give evidence', 'declarar como prueba', 'say evidence', 454),
    ('serve a sentence', 'cumplir condena', 'do a sentence', 455),
    ('take a risk', 'asumir un riesgo', 'do a risk', 458),
    ('make a decision', 'tomar una decisión', 'do a decision', 459),
    ('issue a summons', 'emitir una citación oficial', 'give a summons', 1110),
    ('cooperate with the police', 'cooperar con la policía', 'cooperate to the police', 569),
    ('take someone into custody', 'poner bajo custodia', 'take someone in custody', 573),
    ('be under arrest', 'estar detenido', 'be in arrest', 577),
    ('be on the run', 'estar huido o a la fuga', 'be in the run', 579),
    ('be released on bail', 'quedar en libertad bajo fianza', 'be in bail', 581),
    ('break into a house', 'entrar forzando en una vivienda o local', 'break in the house', 583),
    ('cordon off an area', 'acordonar una zona', 'cordon an area', 587),
    ('comply with the rules', 'cumplir las normas', 'comply the rules', 590),
    ('be charged with a crime', 'ser acusado de un delito', 'be charged of', 594),
    ('plead not guilty to all charges', 'declararse no culpable de todos los cargos', 'plead not guilty of', 598),
]


# ---------- generic helpers ----------

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
    text = re.sub(r'<!--.*?-->', ' ', str(text or ''), flags=re.S)
    text = text.replace('###', ' ')
    return re.sub(r'\s+', ' ', text).strip()


def normalize_option_label(text: str) -> str:
    return compact_text(text).strip(' .;:')


def normalize_key(text: str) -> str:
    return compact_text(text).lower().normalize('NFD') if hasattr(str, 'normalize') else compact_text(text).lower()


def simplify(text: str) -> str:
    return (
        compact_text(text)
        .lower()
        .replace('’', "'")
        .replace('“', '"')
        .replace('”', '"')
        .replace('–', '-')
        .replace('—', '-')
    )


def make_choice_objects(options: list[str]) -> list[dict[str, str]]:
    letters = ['a', 'b', 'c', 'd']
    return [{'key': letters[index], 'label': normalize_option_label(option)} for index, option in enumerate(options[:4])]


def make_option_explanations(choices: list[dict[str, str]], answer_index: int, explanations: dict[str, str] | None = None, *,
                             default_correct: str = 'Es la forma correcta según el documento maestro.',
                             default_incorrect: str = 'No encaja con el enunciado según el documento maestro.'):
    explanations = explanations or {}
    details = []
    for index, choice in enumerate(choices):
        key = choice['key']
        details.append({
            'key': key,
            'label': choice['label'],
            'is_correct': index == answer_index,
            'explanation': compact_text(explanations.get(key) or (default_correct if index == answer_index else default_incorrect)),
        })
    return details


def build_question_item(*, item_id: str, section: str, subsection: str, qtype: str, title: str, prompt: str,
                        choices: list[dict[str, str]], answer_index: int, explanation: str, source_block: str,
                        difficulty: str = 'intermediate', tags: list[str] | None = None, reading_id: str | None = None,
                        option_explanations: list[dict] | None = None, context: str = '', help_text: str = ''):
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
        'option_explanations': option_explanations or [],
        'context': context,
        'help_text': help_text,
        **({'reading_id': reading_id} if reading_id else {}),
    }


def add_fourth_option(options: list[str], extra_pool: list[str], correct_option: str, used: set[str] | None = None) -> list[str]:
    used = used or set()
    result = []
    seen: set[str] = set()
    for option in options:
        cleaned = normalize_option_label(option)
        key = simplify(cleaned)
        if cleaned and key not in seen:
            result.append(cleaned)
            seen.add(key)
    for candidate in extra_pool:
        cleaned = normalize_option_label(candidate)
        key = simplify(cleaned)
        if not cleaned or key in seen or key == simplify(correct_option) or key in used:
            continue
        result.append(cleaned)
        seen.add(key)
        if len(result) == 4:
            return result
    fillers = ['all of a sudden', 'at first sight', 'under control', 'keep a record']
    for filler in fillers:
        key = simplify(filler)
        if key not in seen and key != simplify(correct_option):
            result.append(filler)
            seen.add(key)
        if len(result) == 4:
            break
    return result[:4]


def parse_choice_block(chunk: str) -> list[tuple[str, str]]:
    match = re.search(r'Opciones:\s*(.+?)\s*Respuesta\s+correcta:', chunk, re.I | re.S)
    if not match:
        return []
    segment = compact_text(match.group(1))
    found = re.findall(r'([a-d])\)\s*(.+?)(?=\s+[a-d]\)\s+|$)', segment, re.I)
    return [(key.lower(), normalize_option_label(label)) for key, label in found]


def parse_option_explanations(chunk: str) -> dict[str, str]:
    match = re.search(r'Explicación\s+por\s+opción:\s*(.+)$', chunk, re.I | re.S)
    if not match:
        return {}
    segment = compact_text(match.group(1))
    parsed = {}
    for key, verdict, explanation in re.findall(r'([a-d])\)\s*(Correcta|Incorrecta)\s*:\s*(.+?)(?=\s+[a-d]\)\s*(?:Correcta|Incorrecta)\s*:|$)', segment, re.I):
        parsed[key.lower()] = f'{verdict.capitalize()}: {compact_text(explanation)}'
    return parsed


def find_correct_index(choices: list[str], answer_text: str) -> int:
    answer_text = compact_text(answer_text)
    answer_key_match = re.match(r'([a-d])\)', answer_text, re.I)
    if answer_key_match:
        return ord(answer_key_match.group(1).lower()) - 97
    normalized = simplify(answer_text)
    for index, choice in enumerate(choices):
        if simplify(choice) == normalized:
            return index
    for index, choice in enumerate(choices):
        if simplify(choice) in normalized or normalized in simplify(choice):
            return index
    return 0


# ---------- definition / collocation extraction ----------

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
            distractor_pool.extend([
                candidate['term']
                for candidate in parsed_entries
                if candidate['term'] != entry['term'] and candidate['term'] not in distractor_pool
            ])
            options = add_fourth_option([entry['term']], distractor_pool, entry['term'])
            if len(options) < 4:
                continue
            choices = make_choice_objects(options)
            answer_index = next((i for i, option in enumerate(options) if simplify(option) == simplify(entry['term'])), 0)
            explanations = {}
            for choice in choices:
                if choice['key'] == choices[answer_index]['key']:
                    explanations[choice['key']] = f"Correcta: en el documento, '{entry['term']}' se vincula con '{entry['definition']}'."
                else:
                    explanations[choice['key']] = f"Incorrecta: '{choice['label']}' aparece en el documento, pero no significa '{entry['definition']}'."
            prompt = f"¿Qué expresión encaja mejor con esta idea? {entry['definition']}"
            questions.append(build_question_item(
                item_id=f"def-{slug(section)}-{slug(subsection)}-{index + 1}",
                section=section,
                subsection=subsection,
                qtype='multiple_choice',
                title=f'{subsection} · definición',
                prompt=prompt,
                choices=choices,
                answer_index=answer_index,
                explanation=f"Elemento derivado directamente del documento maestro: {entry['raw']}",
                source_block=f'ingles-definitivo-maestro.md:{entry["line_number"]}',
                tags=[slug(section), 'derived-definition'],
                option_explanations=make_option_explanations(choices, answer_index, explanations),
            ))
    return questions


def extract_curated_collocations() -> list[dict]:
    all_terms = [term for term, _, _, _ in CURATED_COLLOCATIONS]
    items = []
    for index, (term, meaning, typical_mistake, line_number) in enumerate(CURATED_COLLOCATIONS, 1):
        distractor_pool = [candidate for candidate in all_terms if candidate != term]
        options = add_fourth_option([term], distractor_pool, term)
        choices = make_choice_objects(options)
        answer_index = next(i for i, option in enumerate(options) if simplify(option) == simplify(term))
        explanations = {}
        for choice in choices:
            if choice['key'] == choices[answer_index]['key']:
                explanations[choice['key']] = f"Correcta: '{term}' es la collocation o fixed expression recogida en el documento para '{meaning}'."
            elif simplify(choice['label']) == simplify(typical_mistake):
                explanations[choice['key']] = f"Incorrecta: el documento marca '{typical_mistake}' como error típico para esta idea."
            else:
                explanations[choice['key']] = f"Incorrecta: '{choice['label']}' sí aparece en el documento, pero corresponde a otra acción o estructura policial."
        items.append(build_question_item(
            item_id=f'collocation-curated-{index}',
            section='Collocations / Idioms / Fixed Expressions / False Friends',
            subsection='Collocations y Fixed Expressions',
            qtype='multiple_choice',
            title='Collocations policiales',
            prompt=f"¿Qué collocation del documento corresponde a esta idea? {meaning}",
            choices=choices,
            answer_index=answer_index,
            explanation=f"Collocation seleccionada del bloque maestro y contrastada con el error típico '{typical_mistake}'.",
            source_block=f'ingles-definitivo-maestro.md:{line_number}',
            tags=['collocations', 'fixed-expressions', 'curated'],
            option_explanations=make_option_explanations(choices, answer_index, explanations),
        ))
    return items


# ---------- grammar / exam / reading extraction ----------

def extract_grammar_examples(lines: list[str]) -> list[dict]:
    questions = []
    current_headings: list[str] = []
    subsection_examples: dict[str, list[str]] = defaultdict(list)
    raw_examples = []

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
        subsection = current_headings[-1] if current_headings else 'Gramática'
        subsection_examples[subsection].extend([affirmative, negative, interrogative])
        raw_examples.append((line_number, subsection, affirmative, negative, interrogative, line))

    for line_number, subsection, affirmative, negative, interrogative, raw_line in raw_examples:
        title = subsection
        prompts = [
            ('affirmative', '¿Cuál es el ejemplo afirmativo correcto según el documento?', affirmative, [affirmative, negative, interrogative]),
            ('negative', '¿Cuál es el ejemplo negativo correcto según el documento?', negative, [negative, affirmative, interrogative]),
            ('question', '¿Cuál es la pregunta correcta según el documento?', interrogative, [interrogative, affirmative, negative]),
        ]

        extra_pool = [candidate for candidate in subsection_examples[subsection] if candidate not in {affirmative, negative, interrogative}]
        for offset, (label, prompt, answer, options_seed) in enumerate(prompts, 1):
            options = add_fourth_option(options_seed, extra_pool, answer)
            if len(options) < 4:
                continue
            choices = make_choice_objects(options)
            answer_index = find_correct_index(options, answer)
            explanations = {}
            for choice in choices:
                if choice['key'] == choices[answer_index]['key']:
                    explanations[choice['key']] = f'Correcta: el documento presenta exactamente este ejemplo para la forma {label}.'
                else:
                    explanations[choice['key']] = f'Incorrecta: esta opción aparece en el documento, pero no corresponde a la forma {label} pedida.'
            questions.append(build_question_item(
                item_id=f'grammar-{slug(subsection)}-{line_number}-{offset}',
                section='Tiempos verbales y gramática',
                subsection=subsection,
                qtype='grammar_choice',
                title=f'{title} · {label}',
                prompt=prompt,
                choices=choices,
                answer_index=answer_index,
                explanation=f'Ejemplo A/N/Q conservado del documento maestro. Línea original: {raw_line}',
                source_block=f'ingles-definitivo-maestro.md:{line_number}',
                tags=['grammar', slug(subsection), label],
                option_explanations=make_option_explanations(choices, answer_index, explanations),
            ))
    return questions


def extract_exam_items(text: str) -> list[dict]:
    compact = compact_text(text)
    set_titles = ['Set 01', 'Set 02', 'Set 03']
    set_slices = []
    for index, title in enumerate(set_titles):
        start = compact.find(title)
        if start == -1:
            continue
        next_positions = [compact.find(next_title, start + len(title)) for next_title in set_titles[index + 1:]]
        next_positions = [position for position in next_positions if position != -1]
        end = min(next_positions) if next_positions else len(compact)
        set_slices.append((title, compact[start:end]))

    items = []
    global_pool: list[str] = []
    parsed_blocks = []
    for title, chunk in set_slices:
        question_chunks = re.findall(r'(\d+\)\s*.*?)(?=\s+\d+\)\s+|$)', chunk)
        for raw_chunk in question_chunks:
            raw_chunk = compact_text(raw_chunk)
            choices_parsed = parse_choice_block(raw_chunk)
            if not choices_parsed:
                continue
            options = [label for _, label in choices_parsed]
            answer_match = re.search(r'Respuesta\s+correcta:\s*(.+?)(?:\s+Explicación\s+por\s+opción:|$)', raw_chunk, re.I)
            answer_text = compact_text(answer_match.group(1)) if answer_match else ''
            explanation_map = parse_option_explanations(raw_chunk)
            stem = compact_text(re.split(r'Opciones:', raw_chunk, flags=re.I)[0])
            stem = re.sub(r'^\d+\)\s*', '', stem).strip(' .')
            parsed_blocks.append((title, stem, options, answer_text, explanation_map, raw_chunk))
            global_pool.extend(options)

    for index, (title, stem, options_seed, answer_text, explanation_map, raw_chunk) in enumerate(parsed_blocks, 1):
        correct_option = options_seed[find_correct_index(options_seed, answer_text)]
        extra_pool = [candidate for candidate in global_pool if candidate not in options_seed]
        options = add_fourth_option(options_seed, extra_pool, correct_option)
        if len(options) < 4:
            continue
        choices = make_choice_objects(options)
        answer_index = next(i for i, option in enumerate(options) if simplify(option) == simplify(correct_option))
        normalized_map = {key.lower(): value for key, value in explanation_map.items()}
        explanations = {}
        for choice in choices:
            if choice['key'] in normalized_map:
                explanations[choice['key']] = normalized_map[choice['key']]
            elif choice['key'] == choices[answer_index]['key']:
                explanations[choice['key']] = 'Correcta: es la opción que resuelve el ítem según la solución del documento.'
            else:
                explanations[choice['key']] = 'Incorrecta: opción añadida a partir del mismo bloque de examen; no completa correctamente la estructura pedida.'
        items.append(build_question_item(
            item_id=f'exam-{slug(title)}-{index}',
            section='Exámenes / sets / simulacros',
            subsection=title,
            qtype='multiple_choice',
            title=f'{title} · Pregunta {index}',
            prompt=stem,
            choices=choices,
            answer_index=answer_index,
            explanation='Pregunta de simulacro convertida a formato tipo test con explicaciones por alternativa.',
            source_block='ingles-definitivo-maestro.md',
            tags=['exam', slug(title)],
            option_explanations=make_option_explanations(choices, answer_index, explanations),
        ))
    return items


def extract_reading_questions(text: str) -> list[dict]:
    items = []

    bag_prompts = [
        ('1', 'What details does the text provide about the atmosphere on the promenade?', 'According to the text, the promenade had a busy and lively atmosphere, with tourists and local people enjoying the evening near the beach.'),
        ('2', 'Why was the handbag stolen so easily?', 'Based on the text, the theft happened easily because the victim left her bag unattended for a short time while she was paying.'),
        ('3', 'What helped the police locate the stolen bag quickly?', 'The witness description and the CCTV images helped the police identify the suspect later that night.'),
        ('4', 'What was recovered from the bag, and what was still missing?', 'The documents and the phone were recovered from the bag, but the cash was still missing.'),
    ]
    bag_pool = [answer for _, _, answer in bag_prompts]
    for number, prompt, answer in bag_prompts:
        distractors = [candidate for _, _, candidate in bag_prompts if candidate != answer]
        options = add_fourth_option([answer], distractors, answer)
        choices = make_choice_objects(options)
        answer_index = find_correct_index(options, answer)
        explanations = {}
        for choice in choices:
            if choice['key'] == choices[answer_index]['key']:
                explanations[choice['key']] = 'Correcta: coincide con la respuesta oficial y con la paráfrasis explicada del reading del paseo marítimo.'
            else:
                explanations[choice['key']] = 'Incorrecta: es información real del mismo reading, pero responde a otra pregunta distinta.'
        items.append(build_question_item(
            item_id=f'reading-bag-{number}',
            section='Reading y Paráfrasis',
            subsection='Reading — Bag Theft on the Promenade',
            qtype='reading_comprehension',
            title=f'Reading — Bag Theft on the Promenade · Pregunta {number}',
            prompt=prompt,
            choices=choices,
            answer_index=answer_index,
            explanation='Respuesta oficial del reading convertida a pregunta tipo test con cuatro alternativas cerradas.',
            source_block='ingles-definitivo-maestro.md:1771-1899',
            tags=['reading', 'bag-theft'],
            reading_id='bag-theft-on-the-promenade',
            option_explanations=make_option_explanations(choices, answer_index, explanations),
            help_text='Elige la paráfrasis que mejor resume la respuesta oficial del documento.',
        ))

    murder_prompts = [
        ('1', 'What primarily contributed to the students’ heightened excitement during the event in Cambridge?', 'According to the text, the students became especially excited because they saw several teachers pretending to die, which made the situation feel much more serious and realistic.'),
        ('2', 'In the narrator’s early experience at the dinner-party mystery, what aspect of the game appealed to them the most?', 'Based on the text, the narrator most enjoyed playing a character and feeling the suspense of having a possible murderer within the group.'),
        ('3', 'What does the narrator imply about the logistics of hosting murder mystery events in public places?', 'As explained in the text, these events have to be held in private spaces so that other customers are not disturbed.'),
        ('4', 'Why does the narrator particularly value historic venues such as castles for their events?', 'According to the text, castles are especially valuable because their atmosphere makes the mystery more dramatic and immersive.'),
    ]
    for number, prompt, answer in murder_prompts:
        distractors = [candidate for _, _, candidate in murder_prompts if candidate != answer]
        options = add_fourth_option([answer], distractors, answer)
        choices = make_choice_objects(options)
        answer_index = find_correct_index(options, answer)
        explanations = {}
        for choice in choices:
            if choice['key'] == choices[answer_index]['key']:
                explanations[choice['key']] = 'Correcta: resume la respuesta explicada del reading 1 sin copiarla palabra por palabra.'
            else:
                explanations[choice['key']] = 'Incorrecta: usa ideas del mismo reading 1, pero responde a otra de las preguntas del bloque.'
        items.append(build_question_item(
            item_id=f'reading-murder-{number}',
            section='Reading y Paráfrasis',
            subsection='Reading 1 — Murder Mystery',
            qtype='reading_comprehension',
            title=f'Reading 1 — Murder Mystery · Pregunta {number}',
            prompt=prompt,
            choices=choices,
            answer_index=answer_index,
            explanation='Respuesta explicada del reading 1 convertida a formato test con cuatro opciones cerradas.',
            source_block='ingles-definitivo-maestro.md:3775-4105',
            tags=['reading', 'murder-mystery'],
            reading_id='reading-1-murder-mystery',
            option_explanations=make_option_explanations(choices, answer_index, explanations),
            help_text='Selecciona la paráfrasis correcta basada en la respuesta modelo del documento.',
        ))

    return items


# ---------- main ----------

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
    question_items.extend(extract_curated_collocations())
    question_items.extend(extract_grammar_examples(lines))
    question_items.extend(extract_exam_items(raw))
    question_items.extend(extract_reading_questions(raw))

    question_items = [item for item in question_items if len(item.get('choices', [])) == 4]

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
        '- `preguntas.json`: banco ampliado de preguntas generado desde el documento maestro y convertido a formato **tipo test de 4 opciones** con explicaciones por alternativa.\n'
        '- Ambos ficheros están pensados para GitHub Pages y carga vía `fetch`.\n',
        encoding='utf-8',
    )

    print(f'guide_items={len(guide_items)}')
    print(f'question_items={len(question_items)}')


if __name__ == '__main__':
    random.seed(7)
    main()
