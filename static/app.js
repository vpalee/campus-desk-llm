'use strict';
const byId = id => document.getElementById(id);
let articles = [];
let busy = false;
function make(tag, text, cls) {
  const el = document.createElement(tag);
  if (text !== undefined) el.textContent = text;
  if (cls) el.className = cls;
  return el;
}
function renderArticles(filter = '') {
  const list = byId('article-list'); list.replaceChildren();
  const matching = articles.filter(a => `${a.title} ${a.category} ${a.text}`.toLowerCase().includes(filter.toLowerCase()));
  for (const a of matching) {
    const row = make('details', undefined, 'article'); row.id = `article-${a.id}`;
    const title = make('summary'); title.append(make('span', a.category, 'category'), document.createTextNode(a.title));
    row.append(title, make('p', a.text)); list.append(row);
  }
  if (!matching.length) list.append(make('p', 'No matching articles. Try another word.'));
}
function showArticle(id) {
  byId('filter').value = ''; renderArticles();
  const row = byId(`article-${id}`); if (!row) return;
  row.open = true; row.classList.add('highlight');
  row.scrollIntoView({behavior:'auto', block:'nearest'});
  row.querySelector('summary').focus();
}
async function ask(event) {
  event.preventDefault(); if (busy) return;
  const question = byId('question').value.trim();
  if (question.length < 3) { byId('question').setCustomValidity('Enter a question of at least 3 characters.'); byId('question').reportValidity(); return; }
  busy = true; byId('ask-button').disabled = true;
  byId('answer').className = ''; byId('answer').textContent = 'Looking through the handbook…';
  byId('sources').replaceChildren(); byId('trace').hidden = true;
  document.querySelector('.answer-section').setAttribute('aria-busy','true'); byId('answer-state').textContent = 'Looking up sources';
  try {
    const response = await fetch('/api/ask', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({question}), signal:AbortSignal.timeout(100000)});
    const data = await response.json();
    if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Please check your question and try again.');
    byId('answer').textContent = data.answer;
    byId('answer-state').textContent = data.status === 'answered' ? 'Answer with sources' : 'Not covered in the handbook';
    if (data.sources.length) byId('sources').append(make('h3','Check the source','source-heading'));
    data.sources.forEach(a => {
      const button = make('button', a.title, 'source-button'); button.type = 'button';
      button.addEventListener('click', () => showArticle(a.id)); byId('sources').append(button);
    });
    const trace = byId('trace-list'); trace.replaceChildren();
    data.trace.forEach(t => trace.append(make('li', `${t.tool === 'search_knowledge' ? `Search: “${t.query}”` : 'Read article'} → ${t.article_ids.length ? t.article_ids.join(', ') : 'no matching evidence'}`)));
    byId('trace').hidden = !data.trace.length;
  } catch (error) {
    byId('answer').className = 'error';
    byId('answer').textContent = error.name === 'TimeoutError' ? 'The lookup timed out. Please try a shorter question.' : error.message || 'The server could not be reached. Check that the app is running and retry.';
    byId('answer-state').textContent = 'Could not complete the lookup';
  } finally {
    busy = false; byId('ask-button').disabled = false;
    document.querySelector('.answer-section').setAttribute('aria-busy','false');
  }
}
byId('ask-form').addEventListener('submit', ask);
byId('question').addEventListener('input', () => byId('question').setCustomValidity(''));
document.querySelectorAll('[data-question]').forEach(button => button.addEventListener('click', () => {byId('question').value = button.dataset.question; byId('question').setCustomValidity(''); byId('question').focus();}));
byId('filter').addEventListener('input', event => renderArticles(event.target.value));
Promise.all([fetch('/api/health').then(r=>r.json()),fetch('/api/articles').then(r=>r.json())]).then(([health, corpus])=>{
  articles = corpus.articles; renderArticles();
  byId('service-status').textContent = health.configured ? 'Class proxy configured · Answers use the demo handbook' : 'Setup needed: add your class proxy credentials to .env, then retry.';
  if (!health.configured) byId('service-status').classList.add('error');
}).catch(()=>{byId('service-status').textContent = 'Cannot reach the app. Start the server and reload this page.';byId('service-status').classList.add('error');});
