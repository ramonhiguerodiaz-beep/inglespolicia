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
    normalized = compact_text(text).strip(' .;:')
    replacements = {
        'studying / one time': 'studying / once',
        'a lots of': 'a great deal of',
    }
    return replacements.get(normalized.lower(), normalized)


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


def canonical_sentence(text: str) -> str:
    return re.sub(r'[^a-z0-9]+', '', simplify(text))


def make_choice_objects(options: list[str]) -> list[dict[str, str]]:
    letters = ['a', 'b', 'c', 'd']
    return [{'key': letters[index], 'label': normalize_option_label(option)} for index, option in enumerate(options[:4])]


def make_option_explanations(choices: list[dict[str, str]], answer_index: int, explanations: dict[str, str] | None = None, *,
                             default_correct: str = 'Es la forma correcta para esta consigna.',
                             default_incorrect: str = 'No encaja con el enunciado propuesto.'):
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
    fillers = ['in the surrounding area', 'within the legal framework', 'under official supervision', 'in a professional context']
    for filler in fillers:
        key = simplify(filler)
        if key not in seen and key != simplify(correct_option):
            result.append(filler)
            seen.add(key)
        if len(result) == 4:
            break
    return result[:4]


def professional_exam_distractor(prompt: str, correct_option: str, existing: list[str]) -> str:
    prompt_l = simplify(prompt)
    correct_l = simplify(correct_option)
    existing_keys = {simplify(option) for option in existing}

    def first_available(candidates: list[str]) -> str | None:
        for candidate in candidates:
            key = simplify(candidate)
            if key and key not in existing_keys and key != correct_l:
                return candidate
        return None

    if '/' in correct_option:
        if 'either' in correct_l or 'neither' in correct_l:
            candidate = first_available(['Either / nor', 'Both / and', 'Neither / and', 'Either / and'])
            if candidate:
                return candidate
        if 'study' in correct_l:
            candidate = first_available(['studying / once', 'to study / twice', 'study / once a week', 'studying / twice'])
            if candidate:
                return candidate
        candidate = first_available(['for / during', 'since / for', 'to / with', 'in / at'])
        if candidate:
            return candidate

    if correct_l in {'to', 'with', 'for', 'near', 'at', 'on', 'in', 'by', 'from'}:
        candidate = first_available(['for', 'with', 'at', 'by', 'from', 'in', 'on'])
        if candidate:
            return candidate

    if any(token in prompt_l for token in ['prefer', 'enjoy', 'avoid', 'consider', 'mind']):
        candidate = first_available(['to be working', 'working regularly', 'to work regularly', 'working on duty'])
        if candidate:
            return candidate

    if any(token in prompt_l for token in ['since', 'for two years', 'for years', 'for a long time']):
        candidate = first_available(['since last year', 'for many months', 'during the last two years', 'since childhood'])
        if candidate:
            return candidate

    if len(correct_option.split()) <= 2:
        candidate = first_available(['rather', 'almost', 'mainly', 'properly'])
        if candidate:
            return candidate

    return first_available([
        'according to procedure',
        'within a short period',
        'under normal circumstances',
        'in the same situation',
    ]) or 'according to procedure'


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
    if cleaned.endswith(('ar', 'er', 'ir')) and len(cleaned) > 4:
        return True
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


def primary_definition(definition: str) -> str:
    cleaned = compact_text(definition)
    cleaned = re.sub(r'\([^)]*\)', '', cleaned)
    for separator in [' / ', '/', ';', ',']:
        if separator in cleaned:
            cleaned = cleaned.split(separator)[0]
            break
    return compact_text(cleaned)


def definition_prompt(section: str, subsection: str, definition: str) -> str:
    label = primary_definition(definition)
    if section == 'Tiempos verbales y gramática' and subsection == 'Irregulares':
        return f'Elige el verbo irregular que mejor expresa esta acción policial: {label}.'
    if section == 'Tiempos verbales y gramática' and subsection == 'Regulares muy Policiales':
        return f'Elige el verbo regular adecuado para esta acción policial: {label}.'
    if section == 'Collocations / Idioms / Fixed Expressions / False Friends':
        return f'¿Qué expresión profesional encaja mejor con esta idea? {label}.'
    return f'¿Qué opción expresa mejor esta idea? {label}.'


def build_definition_explanation(entry: dict) -> str:
    label = primary_definition(entry['definition'])
    return (
        f"La opción correcta expresa '{label}' con precisión. "
        f"En español: '{entry['term']}' = '{label}'."
    )


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
        if section in {'Exámenes / sets / simulacros', 'Collocations / Idioms / Fixed Expressions / False Friends'}:
            continue

        subsection = current_headings[-1] if current_headings else section
        if section == 'Tiempos verbales y gramática' and subsection in {'Irregulares', 'Regulares muy Policiales'}:
            cleaned = compact_text(re.sub(r'^[*\-]\s*', '', line))
            tokens = cleaned.split()
            if len(tokens) < 4:
                continue
            term = compact_text(' '.join(tokens[:3]))
            definition = compact_text(' '.join(tokens[3:]))
        else:
            term, definition = split_term_definition(line)

        if not term or not definition:
            continue

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
        seen_prompts: set[str] = set()
        for index, entry in enumerate(entries):
            definition_label = primary_definition(entry['definition'])
            prompt = definition_prompt(section, subsection, definition_label)
            prompt_key = simplify(prompt)
            if prompt_key in seen_prompts:
                continue
            seen_prompts.add(prompt_key)
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
                    explanations[choice['key']] = (
                        f"Correcta: '{entry['term']}' expresa la idea de '{definition_label}'. "
                        f"En español: '{definition_label}'."
                    )
                else:
                    explanations[choice['key']] = (
                        f"Incorrecta: '{choice['label']}' no expresa la idea principal '{definition_label}'."
                    )
            questions.append(build_question_item(
                item_id=f"def-{slug(section)}-{slug(subsection)}-{index + 1}",
                section=section,
                subsection=subsection,
                qtype='multiple_choice',
                title=f'{subsection} · precisión léxica',
                prompt=prompt,
                choices=choices,
                answer_index=answer_index,
                explanation=build_definition_explanation(entry),
                source_block=f'ingles-definitivo-maestro.md:{entry["line_number"]}',
                tags=[slug(section), 'derived-definition'],
                option_explanations=make_option_explanations(choices, answer_index, explanations),
                context=f'{subsection} · léxico policial esencial',
                help_text='Selecciona la opción con el significado principal más preciso para un examen B1 policial.',
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
                explanations[choice['key']] = f"Correcta: '{term}' es la collocation adecuada para expresar '{meaning}'."
            elif simplify(choice['label']) == simplify(typical_mistake):
                explanations[choice['key']] = f"Incorrecta: '{typical_mistake}' es un error típico en este tipo de estructura."
            else:
                explanations[choice['key']] = f"Incorrecta: '{choice['label']}' corresponde a otra acción o estructura policial."
        items.append(build_question_item(
            item_id=f'collocation-curated-{index}',
            section='Collocations / Idioms / Fixed Expressions / False Friends',
            subsection='Collocations y Fixed Expressions',
            qtype='multiple_choice',
            title='Collocations policiales',
            prompt=f"¿Qué collocation profesional corresponde a esta idea? {meaning}.",
            choices=choices,
            answer_index=answer_index,
            explanation=f"Explicación académica: la combinación correcta es '{term}', una collocation policial estable. Traducción: '{meaning}'. Error típico a evitar: '{typical_mistake}'.",
            source_block=f'ingles-definitivo-maestro.md:{line_number}',
            tags=['collocations', 'fixed-expressions', 'curated'],
            option_explanations=make_option_explanations(choices, answer_index, explanations),
        ))
    return items


# ---------- grammar / exam / reading extraction ----------

def extract_grammar_examples(lines: list[str]) -> list[dict]:
    def is_real_sentence(text: str) -> bool:
        compact = compact_text(text)
        return 'S +' not in compact and len(compact.split()) >= 4

    def infer_focus(affirmative: str, negative: str, interrogative: str) -> tuple[str, str]:
        joined = f'{affirmative} {negative} {interrogative}'.lower()
        if 'used to' in joined:
            return 'Used to', 'hábito o estado pasado que ya no ocurre'
        if 'going to' in joined:
            return 'Going to', 'intención o predicción basada en indicios'
        if re.search(r'\bwill\b', joined):
            return 'Will', 'decisión rápida o promesa'
        if re.search(r'\bhas\b|\bhave\b', joined):
            return 'Present Perfect', 'acción que empezó en el pasado y conecta con el presente'
        if re.search(r'\bhad\b', joined):
            return 'Past Perfect', 'acción anterior a otro momento del pasado'
        if re.search(r'\bwas\b|\bwere\b', joined) and 'when' in joined:
            return 'Past Continuous + when', 'acción en progreso interrumpida por un hecho puntual'
        if joined.startswith('while ') or ' while ' in joined:
            return 'While + Past Continuous', 'dos acciones en desarrollo dentro del mismo marco temporal'
        if re.search(r'\bwas\b|\bwere\b', joined) and re.search(r'ing\b', joined):
            if re.search(r'\b(arrested|committed|submitted|presented)\b', joined):
                return 'Past Passive', 'estilo de informe donde importa el hecho, no el agente'
            return 'Past Continuous', 'acción en progreso en un momento del pasado'
        if re.search(r'\bdoes\b|\bdon’t\b|\bdoesn’t\b', joined) or 'leaves at' in joined:
            return 'Present Simple (future)', 'horario oficial o programación fija'
        if re.search(r'\bam\b|\bis\b|\bare\b', joined) and re.search(r'ing\b', joined):
            return 'Present Continuous (future)', 'plan ya decidido o agenda cerrada'
        if re.search(r'\bwas arrested\b|\bwere submitted\b', joined):
            return 'Past Passive', 'estilo de informe donde importa el hecho, no el agente'
        return 'Past Simple', 'hecho terminado en el pasado'

    sentence_translations = {
        'The officer stopped the car.': 'El agente detuvo el vehículo.',
        'The officer didn’t stop the car.': 'El agente no detuvo el vehículo.',
        'Did the officer stop the car?': '¿Detuvo el agente el vehículo?',
        'We were patrolling the area.': 'Estábamos patrullando la zona.',
        'We weren’t patrolling the area.': 'No estábamos patrullando la zona.',
        'Were we patrolling the area?': '¿Estábamos patrullando la zona?',
        'We were checking IDs when the suspect ran away.': 'Estábamos comprobando identificaciones cuando el sospechoso huyó.',
        'We weren’t checking IDs when the suspect ran away.': 'No estábamos comprobando identificaciones cuando el sospechoso huyó.',
        'Were we checking IDs when the suspect ran away?': '¿Estábamos comprobando identificaciones cuando el sospechoso huyó?',
        'While we were interviewing the witness, another officer called for backup.': 'Mientras entrevistábamos al testigo, otro agente pidió refuerzos.',
        'While we weren’t interviewing the witness, another officer called for backup.': 'Mientras no entrevistábamos al testigo, otro agente pidió refuerzos.',
        'While we were interviewing the witness, did another officer call for backup?': 'Mientras entrevistábamos al testigo, ¿pidió otro agente refuerzos?',
        'He has provided his ID.': 'Ha entregado su identificación.',
        'He hasn’t provided his ID.': 'No ha entregado su identificación.',
        'Has he provided his ID?': '¿Ha entregado su identificación?',
        'The suspect had left before the police arrived.': 'El sospechoso se había marchado antes de que llegara la policía.',
        'The suspect hadn’t left before the police arrived.': 'El sospechoso no se había marchado antes de que llegara la policía.',
        'Had the suspect left before the police arrived?': '¿Se había marchado el sospechoso antes de que llegara la policía?',
        'He used to work nights.': 'Antes trabajaba de noche.',
        'He didn’t use to work nights.': 'Antes no trabajaba de noche.',
        'Did he use to work nights?': '¿Antes trabajaba de noche?',
        'The suspect was arrested.': 'El sospechoso fue detenido.',
        'The suspect wasn’t arrested.': 'El sospechoso no fue detenido.',
        'Was the suspect arrested?': '¿Fue detenido el sospechoso?',
        'We are leaving tomorrow morning.': 'Nos vamos mañana por la mañana.',
        'We aren’t leaving tomorrow morning.': 'No nos vamos mañana por la mañana.',
        'Are we leaving tomorrow morning?': '¿Nos vamos mañana por la mañana?',
        'The train leaves at 7:45.': 'El tren sale a las 7:45.',
        'The train doesn’t leave at 7:45.': 'El tren no sale a las 7:45.',
        'Does the train leave at 7:45?': '¿Sale el tren a las 7:45?',
        'I will take a taxi.': 'Cogeré un taxi.',
        'I won’t take a taxi.': 'No cogeré un taxi.',
        'Will I take a taxi?': '¿Cogeré un taxi?',
        'He is going to report the incident.': 'Va a denunciar el incidente.',
        'He isn’t going to report the incident.': 'No va a denunciar el incidente.',
        'Is he going to report the incident?': '¿Va a denunciar el incidente?',
    }

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

        for example_chunk in re.split(r'\s+[●•]\s+', line):
            match = re.search(r'A:\s*(.+?)\s+N:\s*(.+?)\s+Q:\s*(.+)', example_chunk)
            if not match:
                continue

            affirmative, negative, interrogative = [compact_text(group) for group in match.groups()]
            if not all(is_real_sentence(example) for example in (affirmative, negative, interrogative)):
                continue

            subsection = current_headings[-1] if current_headings else 'Gramática'
            focus, use_description = infer_focus(affirmative, negative, interrogative)
            subsection_examples[subsection].extend([affirmative, negative, interrogative])
            raw_examples.append({
                'line_number': line_number,
                'subsection': subsection,
                'focus': focus,
                'use_description': use_description,
                'affirmative': affirmative,
                'negative': negative,
                'interrogative': interrogative,
            })

    questions = []
    form_labels = {
        'affirmative': ('forma afirmativa', 'afirmativa'),
        'negative': ('forma negativa', 'negativa'),
        'question': ('forma interrogativa', 'interrogativa'),
    }

    for entry in raw_examples:
        subsection = entry['subsection']
        affirmative = entry['affirmative']
        negative = entry['negative']
        interrogative = entry['interrogative']
        focus = entry['focus']
        use_description = entry['use_description']

        prompts = [
            ('affirmative', f'Elige la frase correcta para expresar {use_description} en {focus}, en forma afirmativa.', affirmative, [affirmative, negative, interrogative]),
            ('negative', f'Elige la frase correcta para expresar {use_description} en {focus}, en forma negativa.', negative, [negative, affirmative, interrogative]),
            ('question', f'Elige la frase correcta para expresar {use_description} en {focus}, en forma interrogativa.', interrogative, [interrogative, affirmative, negative]),
        ]

        extra_pool = [candidate for candidate in subsection_examples[subsection] if candidate not in {affirmative, negative, interrogative}]
        for offset, (label, prompt, answer, options_seed) in enumerate(prompts, 1):
            options = add_fourth_option(options_seed, extra_pool, answer)
            if len(options) < 4:
                continue
            choices = make_choice_objects(options)
            answer_index = find_correct_index(options, answer)
            target_form_label, short_form = form_labels[label]
            explanations = {}
            for choice in choices:
                if choice['key'] == choices[answer_index]['key']:
                    translation = sentence_translations.get(choice['label'], '')
                    explanations[choice['key']] = (
                        f"Correcta: usa {focus} con la {short_form} pedida y mantiene la estructura propia de este tiempo verbal."
                        + (f" Traducción: {translation}" if translation else '')
                    )
                elif canonical_sentence(choice['label']) == canonical_sentence(affirmative):
                    explanations[choice['key']] = f'Incorrecta: la oración está bien construida, pero aparece en forma afirmativa y aquí se pide {target_form_label}.' if label != 'affirmative' else f'Incorrecta: aunque es afirmativa, no resuelve la consigna concreta de este ítem.'
                elif canonical_sentence(choice['label']) == canonical_sentence(negative):
                    explanations[choice['key']] = f'Incorrecta: la oración está bien construida, pero aparece en forma negativa y aquí se pide {target_form_label}.' if label != 'negative' else f'Incorrecta: aunque es negativa, no resuelve la consigna concreta de este ítem.'
                elif canonical_sentence(choice['label']) == canonical_sentence(interrogative):
                    explanations[choice['key']] = f'Incorrecta: la oración está bien construida, pero aparece en forma interrogativa y aquí se pide {target_form_label}.' if label != 'question' else f'Incorrecta: aunque es interrogativa, no resuelve la consigna concreta de este ítem.'
                else:
                    other_focus, _ = infer_focus(choice['label'], choice['label'], choice['label'])
                    explanations[choice['key']] = f'Incorrecta: es una frase válida, pero pertenece a {other_focus} y no a {focus}.'

            translation = sentence_translations.get(answer, '').rstrip('.')
            explanation = (
                f'Explicación académica: {focus} se utiliza para {use_description}. '
                f'La respuesta correcta presenta la {short_form} adecuada y respeta la estructura exigida en pruebas tipo test.'
                + (f" Traducción del modelo: {translation}." if translation else '')
            )
            questions.append(build_question_item(
                item_id=f'grammar-{slug(focus)}-{entry["line_number"]}-{offset}',
                section='Tiempos verbales y gramática',
                subsection=focus,
                qtype='grammar_choice',
                title=f'{focus} · {target_form_label}',
                prompt=prompt,
                choices=choices,
                answer_index=answer_index,
                explanation=explanation,
                source_block=f'ingles-definitivo-maestro.md:{entry["line_number"]}',
                tags=['grammar', slug(focus), label],
                option_explanations=make_option_explanations(choices, answer_index, explanations),
                context=f'Tiempo verbal: {focus}',
                help_text=f'Pista académica: identifica si el examen pide afirmación, negación o pregunta, y después verifica la estructura de {focus}.',
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
            options.append(professional_exam_distractor(stem, correct_option, options))
        elif len(options_seed) < 4 and simplify(options[-1]) not in {simplify(option) for option in options_seed}:
            options[-1] = professional_exam_distractor(stem, correct_option, options_seed)
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
                explanations[choice['key']] = 'Correcta: es la única opción que completa el enunciado con una estructura gramatical natural y válida en inglés de examen.'
            else:
                explanations[choice['key']] = 'Incorrecta: aunque puede parecer razonable a primera vista, no encaja de forma gramatical o léxica con el contexto exacto del enunciado.'
        items.append(build_question_item(
            item_id=f'exam-{slug(title)}-{index}',
            section='Exámenes / sets / simulacros',
            subsection=title,
            qtype='multiple_choice',
            title=f'{title} · Pregunta {index}',
            prompt=stem,
            choices=choices,
            answer_index=answer_index,
            explanation='Explicación académica: se trata de una pregunta de simulacro adaptada a formato profesional. La respuesta correcta respeta la gramática exigida por el enunciado y las alternativas incorrectas funcionan como distractores verosímiles, no como opciones absurdas.',
            source_block='ingles-definitivo-maestro.md',
            tags=['exam', slug(title)],
            option_explanations=make_option_explanations(choices, answer_index, explanations),
            help_text='Lee la estructura completa, identifica la categoría gramatical que falta y descarta las opciones que no suenen naturales en un examen oficial.',
        ))
    return items


def extract_reading_questions(text: str) -> list[dict]:
    items = []

    bag_prompts = [
        {
            'number': '1',
            'prompt': 'What details does the text provide about the atmosphere on the promenade?',
            'options': [
                'According to the passage, the promenade was busy and cheerful, with tourists and local residents enjoying the evening and watching the sunset by the sea.',
                'The text suggests that the promenade was almost empty because most people had already left after the cafés and shops closed earlier than usual.',
                'The passage focuses on a tense and silent atmosphere created by a heavy storm that forced pedestrians to leave the beach area.',
                'The text mainly describes a police cordon that prevented residents and visitors from walking near the promenade during the evening.',
            ],
            'answer': 0,
            'context': '"The promenade was full of tourists and local residents... taking pictures of the sunset."',
            'explanation': 'Explicación académica: la opción correcta parafrasea la descripción del ambiente general sin copiar literalmente el texto. Traducción orientativa: el paseo estaba animado, concurrido y con gente disfrutando de la tarde junto al mar.',
        },
        {
            'number': '2',
            'prompt': 'Why was the handbag stolen so easily?',
            'options': [
                'The text explains that the theft was easy because the woman left her handbag unattended for a brief moment while she was paying at the café.',
                'The passage indicates that the thief forced the café door open at night and stole the bag after the victim had already gone home.',
                'The text suggests that the victim handed her bag to a stranger who offered to help her carry several shopping bags to the car.',
                'The passage states that the handbag disappeared when the owner dropped it on the promenade and continued walking without noticing it.',
            ],
            'answer': 0,
            'context': '"She had left her handbag on the chair beside her table for a moment while paying the bill."',
            'explanation': 'Explicación académica: la paráfrasis correcta mantiene la causa principal del robo: un descuido breve mientras la víctima pagaba. Traducción orientativa: el bolso fue sustraído porque quedó sin vigilancia durante unos segundos.',
        },
        {
            'number': '3',
            'prompt': 'What helped the police locate the stolen bag quickly?',
            'options': [
                'According to the passage, a witness description together with nearby CCTV footage allowed officers to identify the suspect and find the bag later that night.',
                'The text says that the victim used a mobile phone tracking application that immediately showed the exact location of the handbag on a city map.',
                'The passage explains that the suspect returned voluntarily to the café and admitted taking the bag before any witnesses spoke to the police.',
                'The text suggests that officers found the bag after closing all nearby streets and searching every parked vehicle along the promenade.',
            ],
            'answer': 0,
            'context': '"A witness gave a clear description, and CCTV images from a nearby shop helped the police identify the suspect."',
            'explanation': 'Explicación académica: aquí la clave es combinar dos pruebas del texto, la descripción del testigo y las imágenes de CCTV. Traducción orientativa: ambas pistas permitieron identificar al sospechoso con rapidez.',
        },
        {
            'number': '4',
            'prompt': 'What was recovered from the bag, and what was still missing?',
            'options': [
                'The text states that the documents and the phone were recovered, but the cash had disappeared and was still missing when the bag was found.',
                'According to the passage, the entire bag was recovered intact, including the money, and nothing was missing once the police completed their search.',
                'The text explains that only the victim’s bank cards were recovered, while her documents, her phone and the rest of the bag were never found.',
                'The passage suggests that the police recovered the cash first, but they could not locate the handbag itself or any personal belongings inside it.',
            ],
            'answer': 0,
            'context': '"The handbag was found in a narrow alley, but the cash was missing. Her documents and mobile phone were still inside."',
            'explanation': 'Explicación académica: la opción válida distingue con precisión entre los objetos recuperados y el elemento que faltaba. Traducción orientativa: se recuperaron los documentos y el móvil, pero no el dinero.',
        },
        {
            'number': '5',
            'prompt': 'What does the text suggest about the thief’s priority once the handbag had been stolen?',
            'options': [
                'The passage implies that the thief was mainly interested in obtaining cash quickly, since the bag was abandoned after the money had been taken but the documents and phone were left behind.',
                'The text indicates that the thief’s real objective was to steal the victim’s identity documents in order to use them later, which is why the money was left untouched inside the bag.',
                'According to the passage, the suspect intended to keep the entire handbag as a personal item, but dropped it only because officers physically cornered him in the alley a few seconds later.',
                'The text suggests that the thief wanted the mobile phone most of all, and only threw the bag away after discovering that the device could not be unlocked at the scene.',
            ],
            'answer': 0,
            'context': '"The handbag was found in a narrow alley, but the cash was missing. Her documents and mobile phone were still inside."',
            'explanation': 'Explicación académica: la inferencia correcta sale de comparar lo recuperado con lo que faltaba. Si el dinero desaparece pero el resto queda dentro, el foco del robo era el efectivo, no los documentos.',
            'difficulty': 'advanced',
        },
        {
            'number': '6',
            'prompt': 'Why was the first witness response especially valuable during the investigation?',
            'options': [
                'According to the text, the witness reaction was crucial because it provided officers with an immediate description of the suspect that could later be checked against CCTV images.',
                'The passage shows that the witness became essential because he detained the suspect himself before the police arrived and personally recovered the money from the handbag.',
                'The text suggests that the main value of the witness statement was that it replaced the need to interview the victim, who was unable to remember any relevant detail after the theft.',
                'According to the passage, the witness response mattered mostly because it confirmed that no crime had actually taken place and that the bag had simply been moved by mistake.',
            ],
            'answer': 0,
            'context': '"A witness gave a clear description, and CCTV images from a nearby shop helped the police identify the suspect."',
            'explanation': 'Explicación académica: la respuesta buena conecta dos pruebas distintas y entiende su relación: primero hay una descripción útil y después esa información se refuerza con las imágenes.',
            'difficulty': 'advanced',
        },
        {
            'number': '7',
            'prompt': 'What can be inferred about the officers’ deployment during the incident?',
            'options': [
                'The text implies that the officers divided tasks efficiently, because one part of the response focused on pursuing the suspect while another officer remained with the victim to gather information.',
                'The passage indicates that all officers stayed with the victim at the café until a senior inspector arrived and authorised any attempt to search the surrounding streets.',
                'The text suggests that the patrol abandoned the chase almost immediately because they considered recovering the handbag less important than taking written statements first.',
                'According to the passage, the officers waited for a forensic team before moving, as they believed any immediate pursuit might damage physical evidence on the promenade.',
            ],
            'answer': 0,
            'context': '"One officer stayed with the victim while the others searched the area where the suspect had been seen running."',
            'explanation': 'Explicación académica: aquí no se pregunta un dato aislado, sino una deducción organizativa. El fragmento deja ver una actuación coordinada y simultánea, no una respuesta pasiva o desordenada.',
            'difficulty': 'advanced',
        },
        {
            'number': '8',
            'prompt': 'Which statement best captures how different sources of evidence worked together in the case?',
            'options': [
                'The passage shows that the investigation advanced because eyewitness information and shop-camera footage complemented each other, allowing the police to trace the suspect’s movements more reliably.',
                'The text explains that the case depended entirely on the victim’s memory, since the available cameras were damaged and no independent witness was able to describe what had happened.',
                'According to the passage, the police solved the theft mainly through forensic analysis of fingerprints on the café chair where the handbag had been left for a short time.',
                'The text suggests that evidence from local businesses created confusion, because it contradicted every witness version and forced the officers to close the case without an arrest.',
            ],
            'answer': 0,
            'context': '"A witness gave a clear description, and CCTV images from a nearby shop helped the police identify the suspect."',
            'explanation': 'Explicación académica: la mejor paráfrasis expresa cooperación entre pruebas humanas y tecnológicas. Los distractores fallan porque sustituyen esa combinación por pruebas no mencionadas o por una conclusión contraria.',
            'difficulty': 'advanced',
        },
    ]
    for item in bag_prompts:
        choices = make_choice_objects(item['options'])
        answer_index = item['answer']
        explanations = {}
        for idx, choice in enumerate(choices):
            if idx == answer_index:
                explanations[choice['key']] = 'Correcta: esta opción reformula la información esencial del fragmento con otras palabras y mantiene el mismo significado en español.'
            else:
                explanations[choice['key']] = 'Incorrecta: puede sonar plausible, pero añade datos que el texto no dice o altera la idea principal del fragmento.'
        items.append(build_question_item(
            item_id=f"reading-bag-{item['number']}",
            section='Reading y Paráfrasis',
            subsection='Reading — Bag Theft on the Promenade',
            qtype='reading_comprehension',
            title=f"Reading — Bag Theft on the Promenade · Pregunta {item['number']}",
            prompt=item['prompt'],
            choices=choices,
            answer_index=answer_index,
            explanation=item['explanation'],
            source_block='ingles-definitivo-maestro.md:1771-1899',
            tags=['reading', 'bag-theft'],
            reading_id='bag-theft-on-the-promenade',
            option_explanations=make_option_explanations(choices, answer_index, explanations),
            context=item['context'],
            difficulty=item.get('difficulty', 'intermediate'),
            help_text='Fragmento clave del reading: usa esta pista y elige la paráfrasis más fiel al texto. Fíjate en la idea principal y evita opciones que añadan información no mencionada.',
        ))

    murder_prompts = [
        {
            'number': '1',
            'prompt': 'What primarily contributed to the students’ heightened excitement during the event in Cambridge?',
            'options': [
                'According to the text, the students became especially excited when they saw teachers acting as victims, because that made the whole event feel more realistic and dramatic.',
                'The passage suggests that the students were mainly excited because they were allowed to leave lessons early and spend the entire afternoon outside the classroom.',
                'The text explains that the students were impressed above all by the expensive costumes and special effects that had been brought from London for the activity.',
                'The passage indicates that the students were most interested in winning a financial prize that was offered to the group that solved the case first.',
            ],
            'answer': 0,
            'context': '"Several teachers lay on the floor pretending to be dead, which made the scene look much more real to the students."',
            'explanation': 'Explicación académica: la respuesta correcta recoge la causa principal de la emoción de los alumnos y la expresa mediante una reformulación natural. Traducción orientativa: ver a profesores haciendo de víctimas hizo que la actividad pareciera mucho más real.',
        },
        {
            'number': '2',
            'prompt': 'In the narrator’s early experience at the dinner-party mystery, what aspect of the game appealed to them the most?',
            'options': [
                'The narrator was most attracted by the chance to play a character and by the suspense of not knowing whether someone at the table might be the murderer.',
                'The passage shows that the narrator enjoyed the event mainly because the dinner was luxurious and the guests were served by professional actors in costume.',
                'The text suggests that the narrator’s favourite part was collecting physical evidence and comparing fingerprints in a highly technical forensic exercise.',
                'The passage explains that the narrator preferred the event because it required very little interaction and allowed guests to observe quietly from a distance.',
            ],
            'answer': 0,
            'context': '"I loved playing a role and the thrill of wondering whether the murderer might be sitting right next to me."',
            'explanation': 'Explicación académica: la paráfrasis correcta conserva las dos ideas del fragmento: interpretar un papel y sentir suspense dentro del grupo. Traducción orientativa: al narrador le atraían el juego de rol y la intriga de no saber quién era el asesino.',
        },
        {
            'number': '3',
            'prompt': 'What does the narrator imply about the logistics of hosting murder mystery events in public places?',
            'options': [
                'The text implies that these events should be organised in private venues so that regular customers are not disturbed by the performance and the investigation.',
                'The passage argues that public restaurants are the best choice because random customers can join the mystery and make the story more unpredictable.',
                'The text suggests that large shopping centres are ideal locations since background noise helps participants concentrate on the clues more effectively.',
                'The narrator explains that public venues are only a problem when actors are inexperienced, but suitable if the script is short and easy to follow.',
            ],
            'answer': 0,
            'context': '"We usually need private spaces because the event can disturb other customers if it is held in a normal public venue."',
            'explanation': 'Explicación académica: la opción válida deduce correctamente la exigencia logística del texto: estos eventos funcionan mejor en espacios privados. Traducción orientativa: se prefieren lugares privados para no molestar a otros clientes.',
        },
        {
            'number': '4',
            'prompt': 'Why does the narrator particularly value historic venues such as castles for their events?',
            'options': [
                'According to the text, historic places such as castles enhance the atmosphere of the event and make the mystery feel more immersive, dramatic and memorable.',
                'The passage states that castles are preferred mainly because they offer lower rental prices and can host larger groups without any prior decoration work.',
                'The text suggests that old venues are useful above all because their modern surveillance systems make it easier to control participants during the event.',
                'The narrator explains that castles are chosen chiefly because they are easier to reach by public transport than hotels, restaurants or conference halls.',
            ],
            'answer': 0,
            'context': '"Castles and other historic venues create exactly the kind of atmosphere that makes a murder mystery much more dramatic."',
            'explanation': 'Explicación académica: la paráfrasis correcta se centra en el valor ambiental del espacio histórico, que intensifica la experiencia narrativa. Traducción orientativa: los castillos aportan una atmósfera que vuelve el misterio más inmersivo y dramático.',
        },
        {
            'number': '5',
            'prompt': 'What does the text imply about the narrator’s professional role in these events?',
            'options': [
                'The passage suggests that the narrator is involved in more than one aspect of the business, since they do not simply perform but also help design and organise the overall experience.',
                'The text states that the narrator only appears briefly at the end of each evening to present a prize and has no part in the scripts, actors or preparation of the venue.',
                'According to the passage, the narrator mainly works as a police consultant who checks whether the fictional investigations follow real forensic procedure in every detail.',
                'The text implies that the narrator is responsible only for catering arrangements, while the dramatic side of each event is outsourced to independent theatre companies.',
            ],
            'answer': 0,
            'context': '"I write the scripts, hire the actors and help organise the event from start to finish."',
            'explanation': 'Explicación académica: la inferencia correcta resume varias tareas en una sola idea global: el narrador tiene un papel amplio de diseño y coordinación, no una función mínima o puramente técnica.',
            'difficulty': 'advanced',
        },
        {
            'number': '6',
            'prompt': 'Why is staying in character presented as such an important part of the experience?',
            'options': [
                'According to the text, remaining in character helps preserve the illusion of the mystery, so participants respond as if the situation were part of a believable investigation rather than a simple classroom exercise.',
                'The passage suggests that actors must stay in character mainly because they are not allowed to speak to students directly until the police arrive and formally interview them one by one.',
                'The text indicates that staying in character matters only for safety reasons, as smiling or moving too early could cause participants to stop eating during the dinner service.',
                'According to the passage, the narrator insists on staying in character because the script depends on memorising technical legal vocabulary that guests are later asked to repeat in writing.',
            ],
            'answer': 0,
            'context': '"I had to lie there and avoid smiling so the students would believe the scene and take the mystery seriously."',
            'explanation': 'Explicación académica: la respuesta válida conecta la conducta del narrador con el efecto buscado en los participantes: credibilidad. Las otras opciones añaden reglas o fines que el texto no menciona.',
            'difficulty': 'advanced',
        },
        {
            'number': '7',
            'prompt': 'What broader appeal of murder mystery evenings can be inferred from the narrator’s description?',
            'options': [
                'The passage indicates that these events attract people because they combine entertainment with active participation, allowing guests to question suspects, share clues and solve the case themselves.',
                'The text suggests that the main attraction is the possibility of learning formal police procedure in a highly accurate training environment supervised by serving officers.',
                'According to the passage, guests attend mostly for the competitive financial reward offered to the winning table rather than for the dramatic or social side of the evening.',
                'The text implies that participants prefer the events because they can remain silent observers throughout the dinner and are not expected to interact with anyone around them.',
            ],
            'answer': 0,
            'context': '"Guests question suspects, compare clues at their tables and try to decide who the murderer is before the end of the evening."',
            'explanation': 'Explicación académica: la clave está en captar el atractivo general del formato: no es solo ver una historia, sino implicarse en ella. Por eso la opción correcta combina diversión y participación activa.',
            'difficulty': 'advanced',
        },
        {
            'number': '8',
            'prompt': 'How does the police element function within the structure of the event?',
            'options': [
                'The text suggests that the police element intensifies suspense and gives the evening a stronger investigative frame, because questioning suspects and examining clues make guests feel part of an unfolding case.',
                'The passage explains that the police element is included purely for comic relief, since the officers deliberately interrupt the story to make fun of the guests’ theories.',
                'According to the text, the arrival of the police serves mainly to end the game quickly, because once they appear participants are no longer allowed to discuss the case.',
                'The passage indicates that the police element is optional and usually removed from the programme whenever the venue has limited space for costumes and props.',
            ],
            'answer': 0,
            'context': '"The arrival of the police, the questioning of suspects and the collection of clues add another layer of excitement to the evening."',
            'explanation': 'Explicación académica: la buena opción entiende la función narrativa del componente policial: aumentar la tensión y reforzar la sensación de investigación. No es un detalle decorativo ni un cierre brusco.',
            'difficulty': 'advanced',
        },
    ]
    for item in murder_prompts:
        choices = make_choice_objects(item['options'])
        answer_index = item['answer']
        explanations = {}
        for idx, choice in enumerate(choices):
            if idx == answer_index:
                explanations[choice['key']] = 'Correcta: es una paráfrasis fiel del texto, ya que mantiene la idea central y la reformula con vocabulario distinto.'
            else:
                explanations[choice['key']] = 'Incorrecta: esta alternativa introduce matices ajenos al reading o desplaza el foco hacia una información secundaria o inventada.'
        items.append(build_question_item(
            item_id=f"reading-murder-{item['number']}",
            section='Reading y Paráfrasis',
            subsection='Reading 1 — Murder Mystery',
            qtype='reading_comprehension',
            title=f"Reading 1 — Murder Mystery · Pregunta {item['number']}",
            prompt=item['prompt'],
            choices=choices,
            answer_index=answer_index,
            explanation=item['explanation'],
            source_block='ingles-definitivo-maestro.md:3775-4105',
            tags=['reading', 'murder-mystery'],
            reading_id='reading-1-murder-mystery',
            option_explanations=make_option_explanations(choices, answer_index, explanations),
            context=item['context'],
            difficulty=item.get('difficulty', 'intermediate'),
            help_text='Fragmento clave del reading: identifica la idea principal y escoge la opción que la reformula con precisión, sin copiarla ni añadir información nueva.',
        ))

    return items


# ---------- difficulty upgrades ----------

DERIVED_ITEM_FIXES = {
    'def-situaciones-funcionales-preguntas-de-examen-2': {
        'correct_label': 'take someone into custody',
        'prompt_label': 'poner bajo custodia / detener',
    },
    'def-situaciones-funcionales-preguntas-de-examen-3': {
        'correct_label': 'be caught red-handed',
        'prompt_label': 'pillado in fraganti',
    },
    'def-situaciones-funcionales-preguntas-de-examen-8': {
        'prompt_label': 'reunir / recopilar pruebas',
    },
    'def-situaciones-funcionales-preguntas-de-examen-9': {
        'correct_label': 'question / interrogate a suspect',
        'prompt_label': 'interrogar a un sospechoso',
    },
    'def-situaciones-funcionales-preguntas-de-examen-10': {
        'prompt_label': 'redactar / presentar un informe',
    },
    'def-situaciones-funcionales-preguntas-de-examen-17': {
        'prompt_label': 'infracción / violación de la ley',
    },
    'def-situaciones-funcionales-preguntas-de-examen-20': {
        'prompt_label': 'evidencia / información que prueba hechos',
    },
}

DERIVED_FAMILIES = {
    'steal stole stolen': ['steal stole stolen', 'take took taken', 'catch caught caught', 'leave left left'],
    'take took taken': ['take took taken', 'steal stole stolen', 'catch caught caught', 'leave left left'],
    'flee fled fled': ['flee fled fled', 'run ran run', 'leave left left', 'drive drove driven'],
    'run ran run': ['run ran run', 'flee fled fled', 'leave left left', 'drive drove driven'],
    'catch caught caught': ['catch caught caught', 'find found found', 'see saw seen', 'take took taken'],
    'find found found': ['find found found', 'see saw seen', 'hear heard heard', 'catch caught caught'],
    'leave left left': ['leave left left', 'flee fled fled', 'run ran run', 'drive drove driven'],
    'drive drove driven': ['drive drove driven', 'leave left left', 'run ran run', 'take took taken'],
    'speak spoke spoken': ['speak spoke spoken', 'say said said', 'tell told told', 'hear heard heard'],
    'tell told told': ['tell told told', 'say said said', 'speak spoke spoken', 'hear heard heard'],
    'say said said': ['say said said', 'tell told told', 'speak spoke spoken', 'hear heard heard'],
    'hear heard heard': ['hear heard heard', 'see saw seen', 'say said said', 'speak spoke spoken'],
    'see saw seen': ['see saw seen', 'hear heard heard', 'find found found', 'catch caught caught'],
    'shoot shot shot': ['shoot shot shot', 'catch caught caught', 'drive drove driven', 'run ran run'],
    'ring rang rung': ['ring rang rung', 'hear heard heard', 'say said said', 'see saw seen'],
    'arrest arrested arrested': ['arrest arrested arrested', 'detain detained detained', 'question questioned questioned', 'search searched searched'],
    'report reported reported': ['report reported reported', 'issue issued issued', 'confirm confirmed confirmed', 'question questioned questioned'],
    'identify identified identified': ['identify identified identified', 'confirm confirmed confirmed', 'question questioned questioned', 'approach approached approached'],
    'check checked checked': ['check checked checked', 'search searched searched', 'identify identified identified', 'confirm confirmed confirmed'],
    'search searched searched': ['search searched searched', 'seize seized seized', 'check checked checked', 'question questioned questioned'],
    'seize seized seized': ['seize seized seized', 'search searched searched', 'issue issued issued', 'arrest arrested arrested'],
    'issue issued issued': ['issue issued issued', 'report reported reported', 'confirm confirmed confirmed', 'arrest arrested arrested'],
    'escort escorted escorted': ['escort escorted escorted', 'approach approached approached', 'arrest arrested arrested', 'question questioned questioned'],
    'question questioned questioned': ['question questioned questioned', 'identify identified identified', 'report reported reported', 'arrest arrested arrested'],
    'approach approached approached': ['approach approached approached', 'escort escorted escorted', 'identify identified identified', 'question questioned questioned'],
    'incident incidente /': ['incident', 'crime', 'offense', 'crime scene'],
    'evidence': ['evidence', 'proof', 'clues', 'footage'],
    'eyewitness': ['eyewitness', 'security guard', 'police officers', 'suspect'],
    'police officers': ['police officers', 'security guard', 'eyewitness', 'suspect'],
    'security guard': ['security guard', 'police officers', 'eyewitness', 'assistant manager'],
    'crime / offence': ['crime / offence', 'incident', 'offense', 'felony'],
    'crime scene': ['crime scene', 'police station', 'incident', 'evidence'],
    'police station': ['police station', 'crime scene', 'jail', 'prison'],
    'security camera / cctv': ['security camera / CCTV', 'footage', 'evidence', 'crime scene'],
    'footage': ['footage', 'evidence', 'proof', 'security camera / CCTV'],
    'investigate': ['investigate', 'question', 'examine', 'follow'],
    'question': ['question', 'investigate', 'examine', 'confirm'],
    'collect (evidence)': ['collect (evidence)', 'confirm', 'examine', 'follow'],
    'confirm': ['confirm', 'identify', 'check', 'question'],
    'follow': ['follow', 'approach', 'escort', 'contact'],
    'stop': ['stop', 'approach', 'escort', 'follow'],
    'escort': ['escort', 'approach', 'follow', 'contact'],
    'approach': ['approach', 'escort', 'contact', 'follow'],
    'examine': ['examine', 'check', 'confirm', 'question'],
    'contact': ['contact', 'question', 'confirm', 'approach'],
    'flee / run away': ['flee / run away', 'approach', 'follow', 'stop'],
    'busy': ['busy', 'crowded', 'agitated', 'in a hurry'],
    'crowded': ['crowded', 'busy', 'agitated', 'sunny'],
    'sunny': ['sunny', 'busy', 'crowded', 'agitated'],
    'in a hurry': ['in a hurry', 'agitated', 'busy', 'crowded'],
    'agitated': ['agitated', 'in a hurry', 'busy', 'crowded'],
    'be under arrest': ['be under arrest', 'take someone into custody', 'be caught red-handed', 'book someone'],
    'take someone into custody': ['take someone into custody', 'be under arrest', 'book someone', 'press charges'],
    'be caught red-handed': ['be caught red-handed', 'be under arrest', 'get away with it', 'break the law'],
    'book someone': ['book someone', 'take someone into custody', 'press charges', 'file a report'],
    'get away with it': ['get away with it', 'break the law', 'be caught red-handed', 'bend the law'],
    'crack the case': ['crack the case', 'follow a lead', 'uncover', 'gather evidence'],
    'follow a lead': ['follow a lead', 'gather evidence', 'question / interrogate a suspect', 'crack the case'],
    'gather evidence': ['gather evidence', 'file a report', 'press charges', 'follow a lead'],
    'question / interrogate a suspect': ['question / interrogate a suspect', 'file a report', 'press charges', 'follow a lead'],
    'file a report': ['file a report', 'press charges', 'gather evidence', 'question / interrogate a suspect'],
    'press charges': ['press charges', 'file a report', 'book someone', 'break the law'],
    'break the law': ['break the law', 'bend the law', 'get away with it', 'press charges'],
    'uncover': ['uncover', 'crack the case', 'follow a lead', 'gather evidence'],
    'bend the law': ['bend the law', 'break the law', 'get away with it', 'press charges'],
    'actual': ['actual', 'current', 'present', 'recent'],
    'crime': ['crime', 'offense', 'felony', 'misdemeanor'],
    'offense': ['offense', 'crime', 'felony', 'misdemeanor'],
    'felony': ['felony', 'misdemeanor', 'offense', 'crime'],
    'misdemeanor': ['misdemeanor', 'felony', 'offense', 'crime'],
    'proof': ['proof', 'evidence', 'clues', 'footage'],
    'clues': ['clues', 'evidence', 'proof', 'footage'],
    'prison': ['prison', 'jail', 'police station', 'crime scene'],
    'jail': ['jail', 'prison', 'police station', 'crime scene'],
}

GRAMMAR_OPTION_SETS = {
    'The officer stopped the car.': ['The officer stopped the car.', 'The officer was stopping the car.', 'The officer has stopped the car.', 'The officer stop the car.'],
    'The officer didn’t stop the car.': ['The officer didn’t stop the car.', 'The officer wasn’t stopping the car.', 'The officer hasn’t stopped the car.', 'The officer didn’t stopped the car.'],
    'Did the officer stop the car?': ['Did the officer stop the car?', 'Was the officer stop the car?', 'Did the officer stopped the car?', 'Has the officer stop the car?'],
    'We were patrolling the area.': ['We were patrolling the area.', 'We patrolled the area.', 'We are patrolling the area.', 'We were patrol the area.'],
    'We weren’t patrolling the area.': ['We weren’t patrolling the area.', 'We didn’t patrol the area.', 'We aren’t patrolling the area.', 'We weren’t patrol the area.'],
    'Were we patrolling the area?': ['Were we patrolling the area?', 'Did we patrolling the area?', 'Were we patrol the area?', 'Are we patrolling the area?'],
    'We were checking IDs when the suspect ran away.': ['We were checking IDs when the suspect ran away.', 'We checked IDs when the suspect was running away.', 'We were checking IDs when the suspect was run away.', 'We were checking IDs when the suspect run away.'],
    'We weren’t checking IDs when the suspect ran away.': ['We weren’t checking IDs when the suspect ran away.', 'We didn’t check IDs when the suspect was running away.', 'We weren’t checking IDs when the suspect run away.', 'We weren’t check IDs when the suspect ran away.'],
    'Were we checking IDs when the suspect ran away?': ['Were we checking IDs when the suspect ran away?', 'Did we checking IDs when the suspect ran away?', 'Were we check IDs when the suspect ran away?', 'Were we checking IDs when did the suspect run away?'],
    'While we were interviewing the witness, another officer called for backup.': ['While we were interviewing the witness, another officer called for backup.', 'While we interviewed the witness, another officer called for backup.', 'While we were interviewing the witness, another officer was calling for backup.', 'While we were interviewing the witness, another officer call for backup.'],
    'While we weren’t interviewing the witness, another officer called for backup.': ['While we weren’t interviewing the witness, another officer called for backup.', 'While we didn’t interview the witness, another officer called for backup.', 'While we weren’t interviewing the witness, another officer was calling for backup.', 'While we weren’t interview the witness, another officer called for backup.'],
    'While we were interviewing the witness, did another officer call for backup?': ['While we were interviewing the witness, did another officer call for backup?', 'While we interviewed the witness, did another officer call for backup?', 'While we were interviewing the witness, did another officer called for backup?', 'While we were interviewing the witness, was another officer call for backup?'],
    'He has provided his ID.': ['He has provided his ID.', 'He provided his ID.', 'He had provided his ID.', 'He has provide his ID.'],
    'He hasn’t provided his ID.': ['He hasn’t provided his ID.', 'He didn’t provide his ID.', 'He hadn’t provided his ID.', 'He hasn’t provide his ID.'],
    'Has he provided his ID?': ['Has he provided his ID?', 'Did he provided his ID?', 'Has he provide his ID?', 'Had he provided his ID?'],
    'The suspect had left before the police arrived.': ['The suspect had left before the police arrived.', 'The suspect left before the police had arrived.', 'The suspect has left before the police arrived.', 'The suspect had leave before the police arrived.'],
    'The suspect hadn’t left before the police arrived.': ['The suspect hadn’t left before the police arrived.', 'The suspect didn’t leave before the police arrived.', 'The suspect hasn’t left before the police arrived.', 'The suspect hadn’t leave before the police arrived.'],
    'Had the suspect left before the police arrived?': ['Had the suspect left before the police arrived?', 'Did the suspect left before the police arrived?', 'Had the suspect leave before the police arrived?', 'Has the suspect left before the police arrived?'],
    'He used to work nights.': ['He used to work nights.', 'He was used to work nights.', 'He use to work nights.', 'He used to working nights.'],
    'He didn’t use to work nights.': ['He didn’t use to work nights.', 'He wasn’t used to work nights.', 'He didn’t used to work nights.', 'He hasn’t used to work nights.'],
    'Did he use to work nights?': ['Did he use to work nights?', 'Was he used to work nights?', 'Did he used to work nights?', 'Has he use to work nights?'],
    'The suspect was arrested.': ['The suspect was arrested.', 'The suspect arrested.', 'The suspect had arrested.', 'The suspect was arresting.'],
    'The suspect wasn’t arrested.': ['The suspect wasn’t arrested.', 'The suspect didn’t arrested.', 'The suspect hasn’t been arrested.', 'The suspect wasn’t arrest.'],
    'Was the suspect arrested?': ['Was the suspect arrested?', 'Did the suspect arrested?', 'Was the suspect arrest?', 'Has the suspect arrested?'],
    'We are leaving tomorrow morning.': ['We are leaving tomorrow morning.', 'We leave tomorrow morning.', 'We will leaving tomorrow morning.', 'We are leave tomorrow morning.'],
    'We aren’t leaving tomorrow morning.': ['We aren’t leaving tomorrow morning.', 'We don’t leave tomorrow morning.', 'We won’t leaving tomorrow morning.', 'We aren’t leave tomorrow morning.'],
    'Are we leaving tomorrow morning?': ['Are we leaving tomorrow morning?', 'Do we leaving tomorrow morning?', 'Are we leave tomorrow morning?', 'Will we leaving tomorrow morning?'],
    'The train leaves at 7:45.': ['The train leaves at 7:45.', 'The train is leaving at 7:45.', 'The train leave at 7:45.', 'The train has left at 7:45.'],
    'The train doesn’t leave at 7:45.': ['The train doesn’t leave at 7:45.', 'The train isn’t leaving at 7:45.', 'The train doesn’t leaves at 7:45.', 'The train hasn’t left at 7:45.'],
    'Does the train leave at 7:45?': ['Does the train leave at 7:45?', 'Is the train leave at 7:45?', 'Does the train leaves at 7:45?', 'Has the train leave at 7:45?'],
    'I will take a taxi.': ['I will take a taxi.', 'I am going to take a taxi.', 'I will taking a taxi.', 'I will took a taxi.'],
    'I won’t take a taxi.': ['I won’t take a taxi.', 'I am not going to take a taxi.', 'I won’t taking a taxi.', 'I won’t took a taxi.'],
    'Will I take a taxi?': ['Will I take a taxi?', 'Am I going to take a taxi?', 'Will I taking a taxi?', 'Will I took a taxi?'],
    'He is going to report the incident.': ['He is going to report the incident.', 'He will report the incident.', 'He is going report the incident.', 'He is going to reported the incident.'],
    'He isn’t going to report the incident.': ['He isn’t going to report the incident.', 'He won’t report the incident.', 'He isn’t going report the incident.', 'He isn’t going to reported the incident.'],
    'Is he going to report the incident?': ['Is he going to report the incident?', 'Will he report the incident?', 'Is he going report the incident?', 'Is he going to reported the incident?'],
}


def normalize_family_key(label: str) -> str:
    return simplify(label).replace('incidente /', '').strip()


def build_semantic_prompt(item: dict, prompt_label: str) -> str:
    if item['subsection'] == 'Irregulares':
        return f'En un contexto policial, elige la serie verbal irregular más precisa para expresar «{prompt_label}» frente a verbos muy cercanos.'
    if item['subsection'] == 'Regulares muy Policiales':
        return f'En un contexto policial, elige la serie verbal regular más precisa para expresar «{prompt_label}» frente a acciones muy parecidas.'
    if item['section'] == 'Situaciones funcionales':
        return f'En inglés policial, selecciona la expresión exacta para «{prompt_label}» y descarta las alternativas cercanas pero no equivalentes.'
    return f'En vocabulario policial, elige la opción más precisa para «{prompt_label}» y descarta sinónimos parciales o términos próximos.'


def build_semantic_explanation(correct_label: str, prompt_label: str, section: str) -> str:
    if section == 'Situaciones funcionales':
        return f'Explicación académica: la respuesta correcta es «{correct_label}», porque expresa exactamente «{prompt_label}». Las demás opciones son cercanas, pero cambian el matiz legal, procesal o léxico.'
    return f'Explicación académica: la respuesta correcta es «{correct_label}», porque corresponde exactamente a «{prompt_label}». Los distractores pertenecen al mismo campo semántico para obligar a distinguir por matiz.'


def upgrade_derived_definition_item(item: dict) -> dict:
    override = DERIVED_ITEM_FIXES.get(item['id'], {})
    correct_label = override.get('correct_label') or item['answer'].split(') ', 1)[1]
    if correct_label == 'incident incidente /':
        correct_label = 'incident'
    prompt_label = override.get('prompt_label') or item['prompt'].rsplit(':', 1)[-1].strip(' .?¿¡')
    prompt_label = re.sub(r'^(?:Qué opción expresa mejor esta idea\??\s*|Elige el verbo irregular que mejor expresa esta acción policial:\s*|Elige el verbo regular adecuado para esta acción policial:\s*)', '', prompt_label, flags=re.I).strip()
    family_key = normalize_family_key(correct_label)
    family = DERIVED_FAMILIES.get(family_key) or DERIVED_FAMILIES.get(simplify(correct_label)) or [correct_label] + [choice['label'] for choice in item['choices'] if choice['label'] != correct_label]
    options = family[:]
    if correct_label not in options:
        options = [correct_label] + options
    deduped = []
    seen = set()
    for option in options:
        option = 'incident' if option == 'incident incidente /' else option
        key = simplify(option)
        if key not in seen:
            deduped.append(option)
            seen.add(key)
    options = deduped[:4]
    if len(options) < 4:
        extras = [('incident' if choice['label'] == 'incident incidente /' else choice['label']) for choice in item['choices'] if simplify('incident' if choice['label'] == 'incident incidente /' else choice['label']) not in seen and simplify('incident' if choice['label'] == 'incident incidente /' else choice['label']) != simplify(correct_label)]
        for extra in extras:
            options.append(extra)
            seen.add(simplify(extra))
            if len(options) == 4:
                break
    choices = make_choice_objects(options)
    answer_index = next(i for i, option in enumerate(options) if simplify(option) == simplify(correct_label))
    explanations = {}
    for choice in choices:
        if choice['key'] == choices[answer_index]['key']:
            explanations[choice['key']] = f'Correcta: «{choice["label"]}» es la equivalencia más precisa para «{prompt_label}» en este contexto.'
        else:
            explanations[choice['key']] = f'Incorrecta: «{choice["label"]}» pertenece al mismo campo léxico, pero no expresa exactamente «{prompt_label}».'
    item.update({
        'prompt': build_semantic_prompt(item, prompt_label),
        'content_es': build_semantic_prompt(item, prompt_label),
        'choices': choices,
        'answer': f"{chr(97 + answer_index)}) {choices[answer_index]['label']}",
        'acceptable_answers': [f"{chr(97 + answer_index)}) {choices[answer_index]['label']}", choices[answer_index]['key']],
        'option_explanations': make_option_explanations(choices, answer_index, explanations),
        'explanation_es': build_semantic_explanation(correct_label, prompt_label, item['section']),
        'help_text': 'Las cuatro opciones son cercanas. Decide por el matiz exacto: procedimiento, gravedad, función policial o significado legal.',
        'difficulty': 'upper-intermediate',
        'context': f"{item['subsection']} · contraste léxico fino",
    })
    return item


def upgrade_grammar_item(item: dict) -> dict:
    correct_label = item['answer'].split(') ', 1)[1]
    options = GRAMMAR_OPTION_SETS.get(correct_label) or GRAMMAR_OPTION_SETS.get(f'{correct_label}.')
    if not options:
        return item
    choices = make_choice_objects(options)
    answer_index = next(i for i, option in enumerate(options) if normalize_option_label(option) == normalize_option_label(correct_label))
    requested_form = 'interrogativa' if 'question' in item.get('tags', []) else 'negativa' if 'negative' in item.get('tags', []) else 'afirmativa'
    explanations = {}
    for choice in choices:
        if choice['key'] == choices[answer_index]['key']:
            explanations[choice['key']] = f'Correcta: mantiene {item["subsection"]} y la forma {requested_form} pedida por el enunciado.'
        else:
            explanations[choice['key']] = f'Incorrecta: parece cercana, pero falla por auxiliar, forma verbal o tiempo respecto a {item["subsection"]}.'
    item.update({
        'choices': choices,
        'answer': f"{chr(97 + answer_index)}) {choices[answer_index]['label']}",
        'acceptable_answers': [f"{chr(97 + answer_index)}) {choices[answer_index]['label']}", choices[answer_index]['key']],
        'option_explanations': make_option_explanations(choices, answer_index, explanations),
        'explanation_es': f'Explicación académica: la opción correcta respeta {item["subsection"]} y la forma {requested_form}. Los distractores conservan una apariencia similar y solo cambian un auxiliar, una terminación o la combinación verbal decisiva.',
        'help_text': f'Las cuatro alternativas están construidas como forma {requested_form}. Revisa auxiliar, orden, terminación y verbo principal.',
        'difficulty': 'upper-intermediate',
    })
    return item


def upgrade_question_bank(question_items: list[dict]) -> list[dict]:
    upgraded = []
    for item in question_items:
        new_item = dict(item)
        tags = set(new_item.get('tags', []))
        if 'derived-definition' in tags:
            new_item = upgrade_derived_definition_item(new_item)
        elif 'grammar' in tags:
            new_item = upgrade_grammar_item(new_item)
        upgraded.append(new_item)
    return upgraded


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
    question_items = upgrade_question_bank(question_items)

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
