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
  textAnswerWrap: document.getElementById('textAnswerWrap'),
  textAnswer: document.getElementById('textAnswer'),
  checkBtn: document.getElementById('checkBtn'),
  nextBtn: document.getElementById('nextBtn'),
  feedbackBox: document.getElementById('feedbackBox'),
  feedbackVerdict: document.getElementById('feedbackVerdict'),
  feedbackAnswer: document.getElementById('feedbackAnswer'),
  feedbackExplanation: document.getElementById('feedbackExplanation'),
  feedbackSource: document.getElementById('feedbackSource'),
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
    .filter((item) => item.kind === 'question' || item.kind === 'exam_item')
    .map(normalizeQuestion);

  buildSectionSelector();
  buildDifficultySelector();
  bindEvents();
  updateGeneratorMeta();
  updateHeaderCounts();
}

function normalizeQuestion(item) {
  const parsedChoices = Array.isArray(item.choices) && item.choices.length
    ? item.choices
    : parseChoicesFromPrompt(item);
  const normalizedAnswer = normalizeText(item.answer || item.model_answer || '');
  const acceptableAnswers = [item.answer, item.model_answer, ...(item.acceptable_answers || [])]
    .filter(Boolean)
    .map(normalizeText);

  return {
    ...item,
    parsedChoices,
    normalizedAnswer,
    acceptableAnswers,
    displayAnswer: getDisplayAnswer(item, parsedChoices),
    explanation: compactText(item.explanation_es || item.model_answer || item.content_es || 'Sin explicación adicional.'),
  };
}

function parseChoicesFromPrompt(item) {
  const source = [item.prompt, item.content_es, item.content_en].filter(Boolean).join(' ');
  const match = source.match(/Opciones:\s*(.+?)(?:Respuesta correcta:|$)/i);
  if (!match) return [];

  return [...match[1].matchAll(/([a-d])\)\s*([^a-d]+?)(?=\s+[a-d]\)|$)/gi)].map(([, key, label]) => ({
    key: key.toLowerCase(),
    label: compactText(label),
  }));
}

function getDisplayAnswer(item, choices) {
  const rawAnswer = compactText(item.answer || item.model_answer || '');
  if (!choices.length) return rawAnswer || 'Revisa la explicación.';

  const key = rawAnswer.match(/^([a-d])\)/i)?.[1]?.toLowerCase() || normalizeText(rawAnswer);
  const found = choices.find((choice) => choice.key === key || normalizeText(choice.label) === key || normalizeText(rawAnswer).includes(normalizeText(choice.label)));
  return found ? `${found.key}) ${found.label}` : rawAnswer;
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
  els.answerForm.addEventListener('submit', handleSubmit);
  els.checkBtn.addEventListener('click', handleCheckClick);
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

  els.generatorMeta.textContent = `${eligible.length} preguntas disponibles · ${Math.min(requested, eligible.length || requested)} por sesión · ${selectedLabel}`;
  els.heroSubtitle.textContent = `Banco actual: ${state.bank.length} preguntas derivadas del documento maestro para bloques reorganizados, exámenes y readings.`;
}

function startSession(forceRandom) {
  const eligible = forceRandom ? [...state.bank] : getEligibleQuestions();
  const requested = getRequestedCount();
  const picked = shuffle([...eligible]).slice(0, Math.min(requested, eligible.length));

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
  els.nextBtn.classList.add('hidden');
  els.checkBtn.classList.remove('hidden');
  els.textAnswerWrap.classList.add('hidden');
  els.textAnswer.value = '';

  els.questionNumber.textContent = String(state.currentIndex + 1);
  els.questionLabel.textContent = `${(question.difficulty || 'intermediate').toUpperCase()} · ${question.section.toUpperCase()}`;
  els.questionSubtitle.textContent = question.subsection || question.section;
  els.questionType.textContent = typeLabel(question);
  els.questionContext.textContent = compactText(question.title || question.section);
  els.questionPrompt.textContent = compactText(question.prompt || question.content_es || 'Responde a la pregunta.').replace(/Opciones:\s*.+$/i, '').trim();
  els.questionHelp.textContent = question.reading_id
    ? `Reading asociado: ${question.reading_id}`
    : compactText((question.tags || []).slice(0, 3).join(' · '));

  if (question.parsedChoices.length) {
    renderChoiceButtons(question);
    els.checkBtn.classList.add('hidden');
  } else {
    els.textAnswerWrap.classList.remove('hidden');
    els.checkBtn.textContent = question.normalizedAnswer ? 'Comprobar' : 'Marcar como revisada';
    els.textAnswer.focus();
  }

  updateHeaderCounts();
}

function renderChoiceButtons(question) {
  question.parsedChoices.forEach((choice) => {
    const button = document.createElement('button');
    button.className = 'option-btn';
    button.type = 'submit';
    button.dataset.value = choice.key;
    button.innerHTML = `<span class="option-btn__key">${choice.key.toUpperCase()}</span><span>${choice.label}</span>`;
    button.addEventListener('click', () => {
      if (state.answered) return;
      setTimeout(() => evaluateCurrent(choice.key), 0);
    });
    els.optionList.appendChild(button);
  });
}

function handleSubmit(event) {
  event.preventDefault();
}

function handleCheckClick(event) {
  event.preventDefault();
  if (state.answered) return;
  const question = state.session[state.currentIndex];
  if (!question || question.parsedChoices.length) return;
  evaluateCurrent(els.textAnswer.value.trim());
}

function evaluateCurrent(userAnswer) {
  const question = state.session[state.currentIndex];
  if (!question) return;

  const reviewOnly = !question.parsedChoices.length && !question.normalizedAnswer;
  if (!reviewOnly && !userAnswer) return;

  let correct = false;
  state.answered = true;
  state.score.reviewed += 1;

  if (!reviewOnly) {
    correct = isCorrectAnswer(question, userAnswer);
    if (correct) state.score.correct += 1;
    else state.score.incorrect += 1;
  }

  markChoices(question, userAnswer);
  showFeedback(question, reviewOnly ? null : correct);
  updateHeaderCounts();
}

function isCorrectAnswer(question, userAnswer) {
  if (question.parsedChoices.length) {
    const normalizedUser = normalizeText(userAnswer);
    const answerKey = (question.answer || '').match(/^([a-d])\)/i)?.[1]?.toLowerCase();
    if (answerKey) return normalizedUser === answerKey;
    return normalizeText(question.displayAnswer).includes(normalizedUser);
  }

  const normalizedUser = normalizeText(userAnswer);
  const allowed = new Set(question.acceptableAnswers.filter(Boolean));
  if (question.normalizedAnswer) allowed.add(question.normalizedAnswer);
  if (question.displayAnswer) allowed.add(normalizeText(question.displayAnswer));

  return [...allowed].some((answer) => answer && (normalizedUser === answer || answer.includes(normalizedUser) || normalizedUser.includes(answer)));
}

function markChoices(question, userAnswer) {
  if (!question.parsedChoices.length) return;
  const answerKey = (question.answer || '').match(/^([a-d])\)/i)?.[1]?.toLowerCase() || normalizeText(question.displayAnswer).charAt(0);
  const selectedKey = normalizeText(userAnswer);

  [...els.optionList.querySelectorAll('.option-btn')].forEach((button) => {
    button.disabled = true;
    const key = button.dataset.value;
    if (key === answerKey) button.classList.add('option-btn--ok');
    if (key === selectedKey && key !== answerKey) button.classList.add('option-btn--error');
  });
}

function showFeedback(question, correct) {
  els.feedbackBox.classList.remove('hidden');
  const reviewOnly = correct === null;
  els.feedbackVerdict.className = `feedback__verdict ${reviewOnly ? 'feedback__verdict--review' : correct ? 'feedback__verdict--ok' : 'feedback__verdict--error'}`;
  els.feedbackVerdict.textContent = reviewOnly ? '📘 Revisada' : correct ? '✅ Correcta' : '❌ Incorrecta';
  els.feedbackAnswer.textContent = reviewOnly ? `Referencia: ${question.displayAnswer}` : `Respuesta correcta: ${question.displayAnswer}`;
  els.feedbackExplanation.textContent = question.explanation;
  els.feedbackSource.textContent = question.source_block || 'Documento maestro';
  els.checkBtn.classList.add('hidden');
  els.nextBtn.classList.remove('hidden');
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
  els.resultSummary.textContent = `${state.score.correct} aciertos · ${state.score.incorrect} fallos · ${state.score.reviewed - state.score.correct - state.score.incorrect} revisadas sin corrección automática · ${state.session.length ? Math.round((state.score.correct / state.session.length) * 100) : 0}% de acierto sobre la sesión.`;
  updateHeaderCounts(true);
}

function resetSession() {
  state.session = [];
  state.currentIndex = 0;
  state.score = { correct: 0, incorrect: 0, reviewed: 0 };
  state.answered = false;
  els.questionCard.classList.add('hidden');
  els.resultCard.classList.add('hidden');
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

function typeLabel(question) {
  const map = {
    multiple_choice: 'VOCABULARIO',
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
