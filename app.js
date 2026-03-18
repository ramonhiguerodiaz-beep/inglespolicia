const state = {
  questions: [],
  readings: new Map(),
  filteredQuestions: [],
  sessionQuestions: [],
  currentIndex: 0,
  score: { correct: 0, incorrect: 0 },
  answeredCurrent: false,
};

const els = {
  sectionFilter: document.getElementById('sectionFilter'),
  typeFilter: document.getElementById('typeFilter'),
  difficultyFilter: document.getElementById('difficultyFilter'),
  modeFilter: document.getElementById('modeFilter'),
  searchInput: document.getElementById('searchInput'),
  sessionStats: document.getElementById('sessionStats'),
  startBtn: document.getElementById('startBtn'),
  shuffleBtn: document.getElementById('shuffleBtn'),
  resetBtn: document.getElementById('resetBtn'),
  progressPanel: document.getElementById('progressPanel'),
  progressTitle: document.getElementById('progressTitle'),
  progressMeta: document.getElementById('progressMeta'),
  progressBar: document.getElementById('progressBar'),
  emptyState: document.getElementById('emptyState'),
  questionCard: document.getElementById('questionCard'),
  questionEyebrow: document.getElementById('questionEyebrow'),
  questionTitle: document.getElementById('questionTitle'),
  questionPills: document.getElementById('questionPills'),
  readingBox: document.getElementById('readingBox'),
  readingText: document.getElementById('readingText'),
  questionPrompt: document.getElementById('questionPrompt'),
  answerForm: document.getElementById('answerForm'),
  choiceList: document.getElementById('choiceList'),
  textAnswerWrap: document.getElementById('textAnswerWrap'),
  textAnswer: document.getElementById('textAnswer'),
  checkBtn: document.getElementById('checkBtn'),
  nextBtn: document.getElementById('nextBtn'),
  feedbackBox: document.getElementById('feedbackBox'),
  feedbackStatus: document.getElementById('feedbackStatus'),
  correctAnswer: document.getElementById('correctAnswer'),
  answerExplanation: document.getElementById('answerExplanation'),
};

async function loadData() {
  const [questionsRes, guideRes] = await Promise.all([
    fetch('preguntas.json'),
    fetch('guia_maestra.json'),
  ]);

  const questionJson = await questionsRes.json();
  const guideJson = await guideRes.json();

  state.questions = questionJson.items
    .filter((item) => item.kind === 'question' || item.kind === 'exam_item')
    .map(normalizeQuestion);

  buildReadingsMap(guideJson.items || []);
  buildFilters();
  updateSessionStats();
}

function normalizeQuestion(item) {
  const parsedChoices = parseChoices(item);
  const normalizedAnswer = normalizeText(item.answer || item.model_answer || '');
  const acceptableAnswers = [
    item.answer,
    item.model_answer,
    ...(item.acceptable_answers || []),
  ]
    .filter(Boolean)
    .map(normalizeText);

  return {
    ...item,
    parsedChoices,
    acceptableAnswers,
    normalizedAnswer,
    displayAnswer: formatCorrectAnswer(item, parsedChoices),
    explanation: buildExplanation(item),
    readingText: '',
  };
}

function buildReadingsMap(guideItems) {
  guideItems
    .filter((item) => item.kind === 'reading_text')
    .forEach((item) => {
      const readingTag = (item.tags || []).find((tag) => tag.startsWith('reading-'));
      if (readingTag) {
        state.readings.set(readingTag, compactText(item.content_es || item.content_en || ''));
      }
    });

  state.questions = state.questions.map((question) => ({
    ...question,
    readingText: question.reading_id ? state.readings.get(question.reading_id) || '' : '',
  }));
}

function parseChoices(item) {
  if (Array.isArray(item.choices) && item.choices.length) return item.choices;

  const source = [item.prompt, item.content_es, item.content_en].filter(Boolean).join(' ');
  const match = source.match(/Opciones:\s*(.+?)(?:Respuesta correcta:|$)/i);
  if (!match) return [];

  return [...match[1].matchAll(/([a-d])\)\s*([^a-d]+?)(?=\s+[a-d]\)|$)/gi)].map(([, key, label]) => ({
    key: key.toLowerCase(),
    label: compactText(label),
  }));
}

function buildExplanation(item) {
  const parts = [item.explanation_es];
  if (item.model_answer && item.model_answer !== item.answer) parts.push(item.model_answer);
  if (item.bad_answers?.length) parts.push(`Errores frecuentes: ${item.bad_answers.join(' · ')}`);
  return parts.filter(Boolean).join(' ');
}

function formatCorrectAnswer(item, choices) {
  const answer = compactText(item.answer || item.model_answer || '');
  if (!choices.length) return answer || 'Revisa la explicación.';

  const keyMatch = answer.match(/^([a-d])\)/i);
  if (keyMatch) {
    const selected = choices.find((choice) => choice.key === keyMatch[1].toLowerCase());
    if (selected) return `${selected.key}) ${selected.label}`;
  }

  const found = choices.find((choice) => normalizeText(answer).includes(normalizeText(choice.label)));
  return found ? `${found.key}) ${found.label}` : answer;
}

function buildFilters() {
  fillSelect(els.sectionFilter, ['all', ...unique(state.questions.map((item) => item.section))], 'Todas');
  fillSelect(els.typeFilter, ['all', ...unique(state.questions.map((item) => item.type))], 'Todos');
  fillSelect(els.difficultyFilter, ['all', ...unique(state.questions.map((item) => item.difficulty))], 'Todas');

  [els.sectionFilter, els.typeFilter, els.difficultyFilter, els.modeFilter].forEach((el) => el.addEventListener('change', updateSessionStats));
  els.searchInput.addEventListener('input', updateSessionStats);
  els.startBtn.addEventListener('click', startPractice);
  els.shuffleBtn.addEventListener('click', () => {
    updateSessionStats();
    state.filteredQuestions = shuffle([...state.filteredQuestions]);
    renderIdleState(`Selección barajada: ${state.filteredQuestions.length} preguntas listas.`);
  });
  els.resetBtn.addEventListener('click', resetFilters);
  els.answerForm.addEventListener('submit', handleCheckAnswer);
  els.nextBtn.addEventListener('click', goToNextQuestion);
}

function getFilteredQuestions() {
  const search = normalizeText(els.searchInput.value);
  let items = state.questions.filter((item) => {
    if (els.sectionFilter.value !== 'all' && item.section !== els.sectionFilter.value) return false;
    if (els.typeFilter.value !== 'all' && item.type !== els.typeFilter.value) return false;
    if (els.difficultyFilter.value !== 'all' && item.difficulty !== els.difficultyFilter.value) return false;
    if (!search) return true;

    const haystack = normalizeText([
      item.section,
      item.subsection,
      item.title,
      item.prompt,
      item.content_es,
      item.explanation,
      ...(item.tags || []),
    ].join(' '));

    return haystack.includes(search);
  });

  if (els.modeFilter.value === 'random') items = shuffle([...items]);
  return items;
}

function updateSessionStats() {
  state.filteredQuestions = getFilteredQuestions();
  const bySection = countDistinct(state.filteredQuestions.map((item) => item.section));
  const byType = countDistinct(state.filteredQuestions.map((item) => item.type));

  els.sessionStats.innerHTML = `
    <span class="stat-pill"><strong>${state.filteredQuestions.length}</strong> preguntas</span>
    <span class="stat-pill"><strong>${bySection}</strong> secciones</span>
    <span class="stat-pill"><strong>${byType}</strong> tipos</span>
  `;

  if (!state.sessionQuestions.length) {
    renderIdleState(state.filteredQuestions.length
      ? `Hay ${state.filteredQuestions.length} preguntas disponibles con los filtros actuales.`
      : 'No hay preguntas con los filtros actuales.');
  }
}

function startPractice() {
  state.filteredQuestions = getFilteredQuestions();
  state.sessionQuestions = [...state.filteredQuestions];
  state.currentIndex = 0;
  state.score = { correct: 0, incorrect: 0 };
  state.answeredCurrent = false;

  if (!state.sessionQuestions.length) {
    renderIdleState('No hay preguntas para iniciar la práctica con esos filtros.');
    return;
  }

  els.progressPanel.classList.remove('hidden');
  els.emptyState.classList.add('hidden');
  els.questionCard.classList.remove('hidden');
  renderQuestion();
}

function renderQuestion() {
  const question = state.sessionQuestions[state.currentIndex];
  if (!question) {
    renderCompletedState();
    return;
  }

  state.answeredCurrent = false;
  els.answerForm.reset();
  els.choiceList.innerHTML = '';
  els.feedbackBox.classList.add('hidden');
  els.nextBtn.classList.add('hidden');
  els.checkBtn.disabled = false;

  els.questionEyebrow.textContent = `${question.section} · ${question.subsection || question.type}`;
  els.questionTitle.textContent = question.title || `Pregunta ${state.currentIndex + 1}`;
  els.questionPrompt.textContent = cleanPrompt(question);

  renderPills(question);
  renderReading(question);
  renderAnswerInput(question);
  renderProgress();
}

function renderPills(question) {
  els.questionPills.innerHTML = '';
  [question.type, question.difficulty, ...(question.tags || []).slice(0, 2)]
    .filter(Boolean)
    .forEach((text) => {
      const pill = document.createElement('span');
      pill.className = 'pill';
      pill.textContent = text;
      els.questionPills.appendChild(pill);
    });
}

function renderReading(question) {
  const text = question.readingText;
  if (!text) {
    els.readingBox.classList.add('hidden');
    els.readingText.textContent = '';
    return;
  }

  els.readingBox.classList.remove('hidden');
  els.readingText.textContent = text;
}

function renderAnswerInput(question) {
  if (question.parsedChoices.length) {
    els.textAnswerWrap.classList.add('hidden');
    question.parsedChoices.forEach((choice) => {
      const label = document.createElement('label');
      label.className = 'choice-item';
      label.innerHTML = `
        <input type="radio" name="choice" value="${choice.key}">
        <span><strong>${choice.key})</strong> ${choice.label}</span>
      `;
      els.choiceList.appendChild(label);
    });
    return;
  }

  els.choiceList.innerHTML = '';
  els.textAnswerWrap.classList.remove('hidden');
}

function handleCheckAnswer(event) {
  event.preventDefault();
  if (state.answeredCurrent) return;

  const question = state.sessionQuestions[state.currentIndex];
  const userAnswer = getUserAnswer(question);
  if (!userAnswer) return;

  const isCorrect = evaluateAnswer(question, userAnswer);
  state.answeredCurrent = true;
  if (isCorrect) state.score.correct += 1;
  else state.score.incorrect += 1;

  els.feedbackBox.classList.remove('hidden');
  els.feedbackStatus.className = `feedback__status ${isCorrect ? 'is-correct' : 'is-incorrect'}`;
  els.feedbackStatus.textContent = isCorrect ? '✅ Correcta' : '❌ Incorrecta';
  els.correctAnswer.textContent = question.displayAnswer;
  els.answerExplanation.textContent = question.explanation || 'Sin explicación adicional.';
  els.nextBtn.classList.remove('hidden');
  els.checkBtn.disabled = true;
  renderProgress();
}

function getUserAnswer(question) {
  if (question.parsedChoices.length) {
    const checked = document.querySelector('input[name="choice"]:checked');
    return checked ? checked.value : '';
  }
  return els.textAnswer.value.trim();
}

function evaluateAnswer(question, userAnswer) {
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

function goToNextQuestion() {
  state.currentIndex += 1;
  renderQuestion();
}

function renderProgress() {
  const total = state.sessionQuestions.length || 1;
  const current = Math.min(state.currentIndex + 1, total);
  const completed = state.score.correct + state.score.incorrect;

  els.progressTitle.textContent = `Pregunta ${current} de ${total}`;
  els.progressMeta.textContent = `${state.score.correct} aciertos · ${state.score.incorrect} fallos · ${total - completed} pendientes`;
  els.progressBar.style.width = `${(completed / total) * 100}%`;
}

function renderCompletedState() {
  els.questionCard.classList.add('hidden');
  els.emptyState.classList.remove('hidden');
  els.emptyState.innerHTML = `
    Sesión terminada. <strong>${state.score.correct}</strong> aciertos y <strong>${state.score.incorrect}</strong> fallos.
    Ajusta filtros o pulsa <strong>Empezar práctica</strong> para hacer otra tanda.
  `;
  renderProgress();
}

function renderIdleState(message) {
  els.questionCard.classList.add('hidden');
  els.emptyState.classList.remove('hidden');
  els.emptyState.innerHTML = message;
}

function resetFilters() {
  els.sectionFilter.value = 'all';
  els.typeFilter.value = 'all';
  els.difficultyFilter.value = 'all';
  els.modeFilter.value = 'sequential';
  els.searchInput.value = '';
  state.sessionQuestions = [];
  state.currentIndex = 0;
  state.score = { correct: 0, incorrect: 0 };
  els.progressPanel.classList.add('hidden');
  updateSessionStats();
}

function cleanPrompt(question) {
  return compactText(question.prompt || question.content_es || 'Responde a la pregunta.').replace(/Opciones:\s*.+$/i, '').trim();
}

function fillSelect(select, options, allLabel) {
  select.innerHTML = '';
  options.forEach((option) => {
    const el = document.createElement('option');
    el.value = option;
    el.textContent = option === 'all' ? allLabel : option;
    select.appendChild(el);
  });
}

function unique(items) {
  return [...new Set(items.filter(Boolean))].sort((a, b) => a.localeCompare(b, 'es'));
}

function countDistinct(items) {
  return new Set(items.filter(Boolean)).size;
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

loadData().catch((error) => {
  renderIdleState(`Error cargando datos: ${error.message}`);
});

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(() => {}));
}
