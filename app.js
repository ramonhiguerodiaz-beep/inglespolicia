const state = {
  guide: [],
  questions: [],
  items: [],
};

const els = {
  summary: document.getElementById('summary'),
  sectionFilter: document.getElementById('sectionFilter'),
  kindFilter: document.getElementById('kindFilter'),
  typeFilter: document.getElementById('typeFilter'),
  datasetFilter: document.getElementById('datasetFilter'),
  searchInput: document.getElementById('searchInput'),
  quickLinks: document.getElementById('quickLinks'),
  readingsList: document.getElementById('readingsList'),
  resultsTitle: document.getElementById('resultsTitle'),
  resultsMeta: document.getElementById('resultsMeta'),
  cards: document.getElementById('cards'),
  cardTemplate: document.getElementById('cardTemplate'),
  resetBtn: document.getElementById('resetBtn'),
};

async function loadData() {
  const [guideRes, questionRes] = await Promise.all([
    fetch('guia_maestra.json'),
    fetch('preguntas.json'),
  ]);
  const guideJson = await guideRes.json();
  const questionJson = await questionRes.json();
  state.guide = guideJson.items;
  state.questions = questionJson.items;
  state.items = [...state.guide, ...state.questions];
  buildSummary(guideJson, questionJson);
  buildFilters(guideJson.top_sections);
  renderReadings();
  render();
}

function buildSummary(guideJson, questionJson) {
  const readings = state.items.filter(item => item.kind === 'reading_text');
  els.summary.innerHTML = `
    <div>
      <h2>Inventario de cobertura</h2>
      <p>La guía conserva el documento maestro completo por bloques y añade un banco de práctica derivado para explotar teoría, vocabulario, grammar, reading, paráfrasis, situaciones funcionales y simulacros.</p>
    </div>
    <div class="summary__grid">
      <div class="metric"><strong>${guideJson.items.length}</strong><span>bloques de guía / referencia</span></div>
      <div class="metric"><strong>${questionJson.items.length}</strong><span>ítems de práctica / examen</span></div>
      <div class="metric"><strong>${state.items.length}</strong><span>items totales estructurados</span></div>
      <div class="metric"><strong>${readings.length}</strong><span>readings conservados</span></div>
    </div>
  `;
}

function buildFilters(topSections) {
  fillSelect(els.sectionFilter, ['all', ...topSections]);
  fillSelect(els.kindFilter, ['all', ...unique(state.items.map(item => item.kind))]);
  fillSelect(els.typeFilter, ['all', ...unique(state.items.map(item => item.type))]);

  els.quickLinks.innerHTML = '';
  topSections.forEach(section => {
    const button = document.createElement('button');
    button.className = 'quick-btn';
    button.textContent = section;
    button.addEventListener('click', () => {
      els.sectionFilter.value = section;
      render();
    });
    els.quickLinks.appendChild(button);
  });

  [els.sectionFilter, els.kindFilter, els.typeFilter, els.datasetFilter].forEach(el => el.addEventListener('change', render));
  els.searchInput.addEventListener('input', render);
  els.resetBtn.addEventListener('click', () => {
    els.sectionFilter.value = 'all';
    els.kindFilter.value = 'all';
    els.typeFilter.value = 'all';
    els.datasetFilter.value = 'all';
    els.searchInput.value = '';
    render();
  });
}

function renderReadings() {
  const readings = state.items.filter(item => item.kind === 'reading_text');
  els.readingsList.innerHTML = '';
  readings.forEach(reading => {
    const chip = document.createElement('span');
    chip.className = 'chip';
    chip.textContent = reading.title;
    els.readingsList.appendChild(chip);
  });
}

function getFilteredItems() {
  const dataset = els.datasetFilter.value;
  const sourceItems = dataset === 'guide' ? state.guide : dataset === 'questions' ? state.questions : state.items;
  const search = els.searchInput.value.trim().toLowerCase();
  return sourceItems.filter(item => {
    if (els.sectionFilter.value !== 'all' && item.section !== els.sectionFilter.value) return false;
    if (els.kindFilter.value !== 'all' && item.kind !== els.kindFilter.value) return false;
    if (els.typeFilter.value !== 'all' && item.type !== els.typeFilter.value) return false;
    if (!search) return true;
    const haystack = [
      item.title, item.prompt, item.content_es, item.content_en,
      item.explanation_es, ...(item.tags || [])
    ].join(' ').toLowerCase();
    return haystack.includes(search);
  });
}

function render() {
  const filtered = getFilteredItems();
  els.resultsTitle.textContent = filtered.length ? 'Contenido filtrado' : 'Sin resultados';
  els.resultsMeta.textContent = `${filtered.length} items visibles · dataset ${els.datasetFilter.value} · sección ${els.sectionFilter.value}`;
  els.cards.innerHTML = '';

  if (!filtered.length) {
    els.cards.innerHTML = '<div class="panel empty-state">No hay resultados con los filtros actuales.</div>';
    return;
  }

  filtered.forEach(item => els.cards.appendChild(renderCard(item)));
}

function renderCard(item) {
  const node = els.cardTemplate.content.firstElementChild.cloneNode(true);
  node.querySelector('.eyebrow').textContent = `${item.section} · ${item.subsection}`;
  node.querySelector('.card__title').textContent = item.title || item.prompt;
  node.querySelector('.card__prompt').textContent = item.prompt || '';
  node.querySelector('.card__content').textContent = item.content_es || item.content_en || 'Sin contenido adicional.';

  const pillGroup = node.querySelector('.pill-group');
  [item.kind, item.type, ...(item.tags || []).slice(0, 2)].filter(Boolean).forEach(text => {
    const pill = document.createElement('span');
    pill.className = 'pill';
    pill.textContent = text;
    pillGroup.appendChild(pill);
  });

  const answerText = [item.answer, item.model_answer, ...(item.acceptable_answers || [])].filter(Boolean).join('\n\n');
  if (answerText) {
    node.querySelector('.details--answer').classList.remove('hidden');
    node.querySelector('.card__answer').textContent = answerText;
  }

  if (item.explanation_es || (item.bad_answers || []).length) {
    node.querySelector('.details--explanation').classList.remove('hidden');
    const explanation = [item.explanation_es, item.bad_answers?.length ? `Bad answers:\n${item.bad_answers.join('\n')}` : '']
      .filter(Boolean)
      .join('\n\n');
    node.querySelector('.card__explanation').textContent = explanation;
  }

  node.querySelector('.card__footer').textContent = `Fuente: ${item.source_block || 'ingles-definitivo-maestro.md'}`;
  return node;
}

function fillSelect(select, options) {
  select.innerHTML = '';
  options.forEach(option => {
    const el = document.createElement('option');
    el.value = option;
    el.textContent = option === 'all' ? 'Todas / todos' : option;
    select.appendChild(el);
  });
}

function unique(items) {
  return [...new Set(items.filter(Boolean))].sort((a, b) => a.localeCompare(b, 'es'));
}

loadData().catch(error => {
  els.cards.innerHTML = `<div class="panel empty-state">Error cargando datos: ${error.message}</div>`;
});


if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(() => {}));
}
