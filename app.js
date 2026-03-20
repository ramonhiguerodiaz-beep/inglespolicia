const MAX_QUESTIONS = 30;

const state = {
  bank: [],
  filtered: [],
  session: [],
  currentIndex: 0,
  score: { correct: 0, incorrect: 0, reviewed: 0 },
  answered: false,
};

const els = {
  progressFill: document.getElementById('progressFill'),
  correctCount: document.getElementById('correctCount'),
  errorCount: document.getElementById('errorCount'),
  questionCounter: document.getElementById('questionCounter'),
  heroSubtitle: document.getElementById('heroSubtitle'),
  sectionGrid: document.getElementById('sectionGrid'),
  questionCountInput: document.getElementById('questionCountInput'),
  difficultySelect: document.getElementById('difficultySelect'),
  generateBtn: document.getElementById('generateBtn'),
  randomBtn: document.getElementById('randomBtn'),
  answerActions: document.querySelector('.answer-actions'),
  generatorMeta: document.getElementById('generatorMeta'),
  generatorCard: document.getElementById('generatorCard'),
  questionCard: document.getElementById('questionCard'),
  questionNumber: document.getElementById('questionNumber'),
  questionLabel: document.getElementById('questionLabel'),
  questionSubtitle: document.getElementById('questionSubtitle'),
  questionType: document.getElementById('questionType'),
  questionContext: document.getElementById('questionContext'),
  questionPrompt: document.getElementById('questionPrompt'),
  questionHelp: document.getElementById('questionHelp'),
  answerForm: document.getElementById('answerForm'),
  optionList: document.getElementById('optionList'),
  nextBtn: document.getElementById('nextBtn'),
  feedbackBox: document.getElementById('feedbackBox'),
  feedbackVerdict: document.getElementById('feedbackVerdict'),
  feedbackAnswer: document.getElementById('feedbackAnswer'),
  feedbackExplanation: document.getElementById('feedbackExplanation'),
  feedbackOptionList: document.getElementById('feedbackOptionList'),
  resultCard: document.getElementById('resultCard'),
  resultCorrect: document.getElementById('resultCorrect'),
  resultTotal: document.getElementById('resultTotal'),
  resultSummary: document.getElementById('resultSummary'),
  restartBtn: document.getElementById('restartBtn'),
};

async function init() {
  const response = await fetch('preguntas.json');
  const payload = await response.json();
  state.bank = (payload.items || [])
    .filter((item) => (item.kind === 'question' || item.kind === 'exam_item') && Array.isArray(item.choices) && item.choices.length === 4)
    .map(normalizeQuestion);

  buildSectionSelector();
  buildDifficultySelector();
  bindEvents();
  updateGeneratorMeta();
  updateHeaderCounts();
}

function normalizeQuestion(item) {
  const parsedChoices = Array.isArray(item.choices) ? item.choices.map((choice) => ({
    key: choice.key,
    label: compactText(choice.label),
  })) : [];
  const optionDetails = Array.isArray(item.option_explanations) && item.option_explanations.length
    ? item.option_explanations.map((detail) => ({
      key: detail.key,
      label: compactText(detail.label),
      isCorrect: Boolean(detail.is_correct),
      explanation: compactText(detail.explanation),
    }))
    : parsedChoices.map((choice, index) => ({
      key: choice.key,
      label: choice.label,
      isCorrect: index === 0,
      explanation: index === 0 ? 'Correcta: es la opción válida para esta consigna.' : 'Incorrecta: no resuelve correctamente la consigna.',
    }));
  const answerKey = (item.answer || '').match(/^([a-d])\)/i)?.[1]?.toLowerCase() || (optionDetails.find((detail) => detail.isCorrect) || {}).key || 'a';
  const answerIndex = Math.max(0, parsedChoices.findIndex((choice) => choice.key === answerKey));
  const cleanedContext = buildContext(item);

  return {
    ...item,
    parsedChoices,
    optionDetails: optionDetails.map((detail) => ({
      ...detail,
      explanation: buildOptionExplanation(item, detail),
    })),
    answerKey,
    answerIndex,
    displayAnswer: parsedChoices[answerIndex] ? `${parsedChoices[answerIndex].key}) ${parsedChoices[answerIndex].label}` : 'Revisa la explicación.',
    explanation: buildMainExplanation(item, parsedChoices[answerIndex], optionDetails),
    context: cleanedContext,
    helpText: buildHelpText(item),
    promptText: buildPrompt(item, cleanedContext),
    priority: computePriority(item),
  };
}

function buildSectionSelector() {
  const sections = [...new Set(state.bank.map((item) => item.section).filter(Boolean))].sort((a, b) => a.localeCompare(b, 'es'));
  els.sectionGrid.innerHTML = '';

  sections.forEach((section, index) => {
    const count = state.bank.filter((item) => item.section === section).length;
    const label = document.createElement('label');
    label.className = 'section-chip';
    label.innerHTML = `
      <input type="checkbox" value="${escapeHtml(section)}" ${index < 4 ? 'checked' : ''}>
      <span>${index + 1}. ${section}</span>
      <small>${count}</small>
    `;
    els.sectionGrid.appendChild(label);
  });
}

function buildDifficultySelector() {
  const levels = [...new Set(state.bank.map((item) => item.difficulty).filter(Boolean))].sort((a, b) => a.localeCompare(b, 'es'));
  levels.forEach((level) => {
    const option = document.createElement('option');
    option.value = level;
    option.textContent = capitalize(level);
    els.difficultySelect.appendChild(option);
  });
}

function bindEvents() {
  els.generateBtn.addEventListener('click', () => startSession(false));
  els.randomBtn.addEventListener('click', () => startSession(true));
  els.answerForm.addEventListener('submit', (event) => event.preventDefault());
  els.nextBtn.addEventListener('click', goToNextQuestion);
  els.restartBtn.addEventListener('click', resetSession);
  els.sectionGrid.addEventListener('change', updateGeneratorMeta);
  els.difficultySelect.addEventListener('change', updateGeneratorMeta);
  els.questionCountInput.addEventListener('input', updateGeneratorMeta);
}

function getSelectedSections() {
  return [...els.sectionGrid.querySelectorAll('input:checked')].map((input) => input.value);
}

function getRequestedCount() {
  const value = Number(els.questionCountInput.value) || MAX_QUESTIONS;
  return Math.max(1, Math.min(MAX_QUESTIONS, value));
}

function getEligibleQuestions() {
  const selectedSections = getSelectedSections();
  const difficulty = els.difficultySelect.value;

  return state.bank.filter((item) => {
    if (selectedSections.length && !selectedSections.includes(item.section)) return false;
    if (difficulty !== 'all' && item.difficulty !== difficulty) return false;
    return true;
  });
}

function updateGeneratorMeta() {
  const selectedSections = getSelectedSections();
  const eligible = getEligibleQuestions();
  const requested = getRequestedCount();
  const selectedLabel = selectedSections.length ? selectedSections.join(' · ') : 'sin filtros por bloque';

  els.generatorMeta.textContent = `${eligible.length} preguntas tipo test disponibles · ${Math.min(requested, eligible.length || requested)} por sesión · ${selectedLabel}`;
  els.heroSubtitle.textContent = `Banco actual: ${state.bank.length} preguntas cerradas de 4 opciones con distractores verosímiles, explicaciones claras en español y enfoque práctico para opositores.`;
}

function startSession(forceRandom) {
  const eligible = forceRandom ? [...state.bank] : getEligibleQuestions();
  const requested = getRequestedCount();
  const picked = forceRandom
    ? shuffle([...eligible]).slice(0, Math.min(requested, eligible.length))
    : pickQuestions(eligible, requested);

  if (!picked.length) {
    els.generatorMeta.textContent = 'No hay preguntas disponibles con esta combinación. Cambia los filtros o usa aleatorio total.';
    return;
  }

  state.session = picked;
  state.filtered = eligible;
  state.currentIndex = 0;
  state.score = { correct: 0, incorrect: 0, reviewed: 0 };
  state.answered = false;

  els.generatorCard.classList.remove('hidden');
  els.questionCard.classList.remove('hidden');
  els.resultCard.classList.add('hidden');
  updateHeaderCounts();
  renderQuestion();
}

function renderQuestion() {
  const question = state.session[state.currentIndex];
  if (!question) {
    renderResults();
    return;
  }

  state.answered = false;
  els.answerForm.reset();
  els.optionList.innerHTML = '';
  els.feedbackBox.classList.add('hidden');
  els.feedbackOptionList.innerHTML = '';
  els.nextBtn.classList.add('hidden');
  els.answerActions.classList.remove('answer-actions--sticky');

  els.questionNumber.textContent = String(state.currentIndex + 1);
  els.questionLabel.textContent = `${(question.difficulty || 'intermediate').toUpperCase()} · ${question.section.toUpperCase()}`;
  els.questionSubtitle.textContent = question.subsection || question.section;
  els.questionType.textContent = typeLabel(question);
  els.questionContext.textContent = question.context;
  els.questionPrompt.textContent = question.promptText;
  els.questionHelp.textContent = question.helpText;

  renderChoiceButtons(question);
  updateHeaderCounts();
  requestAnimationFrame(() => {
    els.questionCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
}

function renderChoiceButtons(question) {
  question.parsedChoices.forEach((choice) => {
    const button = document.createElement('button');
    button.className = 'option-btn';
    button.type = 'button';
    button.dataset.value = choice.key;
    button.innerHTML = `<span class="option-btn__key">${choice.key.toUpperCase()}</span><span>${escapeHtml(choice.label)}</span>`;
    button.addEventListener('click', () => {
      if (state.answered) return;
      evaluateCurrent(choice.key);
    });
    els.optionList.appendChild(button);
  });
}

function evaluateCurrent(userAnswer) {
  const question = state.session[state.currentIndex];
  if (!question || !userAnswer || state.answered) return;

  const correct = question.answerKey === normalizeText(userAnswer);
  state.answered = true;
  state.score.reviewed += 1;
  if (correct) state.score.correct += 1;
  else state.score.incorrect += 1;

  markChoices(question, userAnswer);
  showFeedback(question, correct, userAnswer);
  updateHeaderCounts();
}

function markChoices(question, userAnswer) {
  const selectedKey = normalizeText(userAnswer);
  [...els.optionList.querySelectorAll('.option-btn')].forEach((button) => {
    button.disabled = true;
    const key = button.dataset.value;
    if (key === question.answerKey) button.classList.add('option-btn--ok');
    if (key === selectedKey && key !== question.answerKey) button.classList.add('option-btn--error');
  });
}

function showFeedback(question, correct, userAnswer) {
  els.feedbackBox.classList.remove('hidden');
  els.feedbackVerdict.className = `feedback__verdict ${correct ? 'feedback__verdict--ok' : 'feedback__verdict--error'}`;
  els.feedbackVerdict.textContent = correct ? '✅ Correcta' : '❌ Incorrecta';

  const selectedChoice = question.parsedChoices.find((choice) => choice.key === normalizeText(userAnswer));
  els.feedbackAnswer.textContent = correct
    ? `Has acertado: ${question.displayAnswer}`
    : `Tu elección: ${selectedChoice ? `${selectedChoice.key}) ${selectedChoice.label}` : '-'} · Respuesta correcta: ${question.displayAnswer}`;
  els.feedbackExplanation.textContent = question.explanation;
  renderFeedbackOptions(question, normalizeText(userAnswer));
  els.nextBtn.classList.remove('hidden');
  els.answerActions.classList.add('answer-actions--sticky');

  requestAnimationFrame(() => {
    els.feedbackBox.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
}

function renderFeedbackOptions(question, selectedKey) {
  els.feedbackOptionList.innerHTML = '';
  question.optionDetails.forEach((detail) => {
    const item = document.createElement('article');
    item.className = `feedback-option ${detail.isCorrect ? 'feedback-option--ok' : 'feedback-option--error'}${selectedKey === detail.key ? ' feedback-option--selected' : ''}`;
    item.innerHTML = `
      <div class="feedback-option__header">
        <span class="feedback-option__key">${detail.key.toUpperCase()}</span>
        <strong>${escapeHtml(detail.label)}</strong>
      </div>
      <p>${escapeHtml(detail.explanation)}</p>
    `;
    els.feedbackOptionList.appendChild(item);
  });
}

function goToNextQuestion() {
  state.currentIndex += 1;
  renderQuestion();
}

function renderResults() {
  els.questionCard.classList.add('hidden');
  els.resultCard.classList.remove('hidden');
  els.resultCorrect.textContent = state.score.correct;
  els.resultTotal.textContent = state.session.length;
  els.resultSummary.textContent = `${state.score.correct} aciertos · ${state.score.incorrect} fallos · ${state.session.length ? Math.round((state.score.correct / state.session.length) * 100) : 0}% de acierto. Se ha priorizado una mezcla equilibrada de bloques y preguntas con más contexto.`;
  updateHeaderCounts(true);
}

function resetSession() {
  state.session = [];
  state.currentIndex = 0;
  state.score = { correct: 0, incorrect: 0, reviewed: 0 };
  state.answered = false;
  els.questionCard.classList.add('hidden');
  els.resultCard.classList.add('hidden');
  els.answerActions.classList.remove('answer-actions--sticky');
  updateHeaderCounts();
}

function updateHeaderCounts(finished = false) {
  const total = state.session.length || getRequestedCount();
  const current = finished ? total : Math.min(state.currentIndex + 1, total);
  const answered = state.score.reviewed;
  const percent = total ? (answered / total) * 100 : 0;

  els.correctCount.textContent = state.score.correct;
  els.errorCount.textContent = state.score.incorrect;
  els.questionCounter.textContent = `Pregunta ${current} de ${total}`;
  els.progressFill.style.width = `${percent}%`;
}

function pickQuestions(eligible, requested) {
  const groups = new Map();
  shuffle([...eligible])
    .sort((a, b) => b.priority - a.priority)
    .forEach((item) => {
      const key = item.section || 'General';
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push(item);
    });

  const picked = [];
  const target = Math.min(requested, eligible.length);
  while (picked.length < target) {
    let added = false;
    for (const items of groups.values()) {
      if (!items.length || picked.length >= target) continue;
      picked.push(items.shift());
      added = true;
    }
    if (!added) break;
  }
  return picked;
}

function computePriority(item) {
  let score = 0;
  const prompt = compactText(item.prompt);
  const section = normalizeText(item.section);
  const type = normalizeText(item.type);
  const context = normalizeText(item.context);

  if (item.difficulty === 'advanced') score += 8;
  if (item.reading_id) score += 6;
  if (section.includes('reading')) score += 5;
  if (section.includes('collocations')) score += 4;
  if (section.includes('simulacros')) score += 3;
  if (type.includes('grammar')) score += 2;
  if (/elige el verbo irregular que mejor expresa/i.test(prompt)) score -= 6;
  if (/que opcion expresa mejor esta idea/i.test(normalizeText(prompt))) score -= 4;
  if (context.includes('lexico policial esencial')) score -= 2;

  return score;
}

function buildPrompt(item) {
  const prompt = compactText(item.prompt || 'Selecciona la respuesta correcta.');
  const normalized = normalizeText(prompt);

  if (/elige el verbo irregular que mejor expresa esta accion policial:/i.test(normalized)) {
    const target = prompt.split(':').pop()?.replace(/\.$/, '').trim();
    return target
      ? `¿Qué verbo irregular encaja mejor con la idea de “${target}”?`
      : '¿Qué verbo irregular completa mejor la idea planteada?';
  }

  if (/que opcion expresa mejor esta idea/i.test(normalized)) {
    const target = prompt.split('?').pop()?.replace(/\.$/, '').trim();
    return target
      ? `¿Qué opción transmite mejor “${target}” en inglés policial?`
      : '¿Qué opción transmite mejor la idea propuesta?';
  }

  return prompt
    .replace(/documento maestro/gi, 'material de referencia')
    .replace(/fragmento citado/gi, 'texto')
    .replace(/texto base/gi, 'texto');
}

function buildContext(item) {
  const raw = compactText(item.context || item.reading_excerpt || item.title || item.section);
  return raw
    .replace(/fragmento clave:\s*/gi, '')
    .replace(/documento maestro/gi, 'material de referencia')
    .replace(/\s{2,}/g, ' ')
    .trim();
}

function buildHelpText(item) {
  const help = compactText(item.help_text);
  const normalized = normalizeText(help);

  if (!help) {
    return item.reading_id
      ? 'Apóyate en el contexto y elige la opción que mejor parafrasea la información relevante.'
      : 'Fíjate en el matiz, el uso real y los distractores antes de responder.';
  }

  if (normalized.includes('fragmento citado')) {
    return 'Usa el contexto y descarta la alternativa que solo repite palabras sin responder a la idea principal.';
  }

  if (normalized.includes('significado principal mas preciso')) {
    return 'Elige la alternativa más precisa y evita opciones demasiado generales o parecidas solo en la forma.';
  }

  return help
    .replace(/documento maestro/gi, 'material de referencia')
    .replace(/fragmento citado/gi, 'contexto');
}

function buildMainExplanation(item, correctChoice, optionDetails) {
  const raw = compactText(item.explanation_es || '');
  const sanitized = raw
    .replace(/explicaci[oó]n acad[eé]mica:\s*/gi, '')
    .replace(/elemento derivado directamente del documento maestro:\s*/gi, '')
    .replace(/documento maestro/gi, 'material de referencia')
    .replace(/fragmento citado/gi, 'contexto')
    .trim();

  if (sanitized) return sanitized;

  const correctDetail = optionDetails.find((detail) => detail.isCorrect);
  if (correctDetail?.explanation) return correctDetail.explanation;
  if (correctChoice?.label) return `La correcta es ${correctChoice.key}) ${correctChoice.label} porque es la única opción que responde con precisión a la consigna.`;
  return 'La opción correcta es la única que mantiene el sentido exacto que exige la pregunta.';
}

function buildOptionExplanation(item, detail) {
  const text = compactText(detail.explanation || '');
  const sanitized = text
    .replace(/explicaci[oó]n acad[eé]mica:\s*/gi, '')
    .replace(/elemento derivado directamente del documento maestro:\s*/gi, '')
    .replace(/documento maestro/gi, 'material de referencia')
    .replace(/fragmento citado/gi, 'contexto')
    .trim();

  if (sanitized) return sanitized;
  return detail.isCorrect
    ? 'Es la alternativa válida porque mantiene el significado exacto y encaja en el contexto planteado.'
    : 'No es correcta porque cambia el significado, resulta demasiado general o introduce un matiz incorrecto.';
}

function typeLabel(question) {
  const map = {
    multiple_choice: 'TIPO TEST',
    translation_choice: 'EXPRESIÓN',
    fill_in_the_blank: 'VERBOS',
    reading_comprehension: 'READING',
    grammar_choice: 'GRAMÁTICA',
  };
  return map[question.type] || question.type.replace(/_/g, ' ').toUpperCase();
}

function compactText(text) {
  return String(text || '').replace(/\s+/g, ' ').trim();
}

function normalizeText(text) {
  return compactText(text)
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '');
}

function shuffle(items) {
  for (let i = items.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [items[i], items[j]] = [items[j], items[i]];
  }
  return items;
}

function capitalize(text) {
  return text ? text.charAt(0).toUpperCase() + text.slice(1) : '';
}

function escapeHtml(text) {
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

init().catch((error) => {
  els.generatorMeta.textContent = `Error cargando el banco de preguntas: ${error.message}`;
});

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(() => {}));
}
