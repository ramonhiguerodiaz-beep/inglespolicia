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

  return {
    ...item,
    parsedChoices,
    optionDetails,
    answerKey,
    answerIndex,
    displayAnswer: parsedChoices[answerIndex] ? `${parsedChoices[answerIndex].key}) ${parsedChoices[answerIndex].label}` : 'Revisa la explicación.',
    explanation: compactText(item.explanation_es || 'Sin explicación adicional.'),
    context: compactText(item.context || item.title || item.section),
    helpText: compactText(item.help_text || (item.reading_id ? 'Selecciona la opción que mejor resume la idea principal del texto.' : (item.tags || []).slice(0, 3).join(' · '))),
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
  els.heroSubtitle.textContent = `Banco actual: ${state.bank.length} preguntas cerradas de 4 opciones con explicación académica por alternativa.`;
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
  els.feedbackOptionList.innerHTML = '';
  els.nextBtn.classList.add('hidden');

  els.questionNumber.textContent = String(state.currentIndex + 1);
  els.questionLabel.textContent = `${(question.difficulty || 'intermediate').toUpperCase()} · ${question.section.toUpperCase()}`;
  els.questionSubtitle.textContent = question.subsection || question.section;
  els.questionType.textContent = typeLabel(question);
  els.questionContext.textContent = question.context;
  els.questionPrompt.textContent = compactText(question.prompt || 'Selecciona la respuesta correcta.');
  els.questionHelp.textContent = question.helpText;

  renderChoiceButtons(question);
  updateHeaderCounts();
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
  els.resultSummary.textContent = `${state.score.correct} aciertos · ${state.score.incorrect} fallos · ${state.session.length ? Math.round((state.score.correct / state.session.length) * 100) : 0}% de acierto. Todas las preguntas de esta sesión fueron de 4 opciones cerradas.`;
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
