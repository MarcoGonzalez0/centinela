/**
 * dorks.js
 * - Bootstrap-friendly
 * - Entrada: initGraficosDorks(datos)
 *   datos puede ser:
 *     1) un array de dorks: [ { description, query, results:[{title,snippet,link}], ... }, ... ]
 *     2) un objeto con .results que sea array (por compatibilidad): { results: [...] }
 *
 * - Registra: window.Visuals['dorks'] = initGraficosDorks;
 *
 * - Presentación: lista de cards compactas. Cada card muestra:
 *     - description (arriba)
 *     - query (inline, con botón copiar)
 *     - resumen de cantidad de resultados
 *     - botón "Ver" que despliega la lista de resultados (title, snippet, link)
 *     - botón "Abrir" (abre hasta 5 enlaces)
 *
 * - Nada más: simple, legible y eficaz.
 */

(function () {
  function qs(sel, ctx = document) { return ctx.querySelector(sel); }
  function qsa(sel, ctx = document) { return Array.from((ctx||document).querySelectorAll(sel)); }

  function escapeHTML(s) {
    return String(s ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function renderResultItem(r) {
    const title = escapeHTML(r.title || r.link || 'sin título');
    const href = escapeHTML(r.link || '#');
    const snippet = r.snippet ? `<div class="small text-muted mt-1">${escapeHTML(r.snippet)}</div>` : '';
    return `
      <li class="mb-2">
        <a href="${href}" target="_blank" rel="noopener noreferrer" class="fw-semibold">${title}</a>
        ${snippet}
      </li>
    `;
  }

  function createCardHTML(dork, idx) {
    const results = Array.isArray(dork.results) ? dork.results : [];
    const count = results.length;
    const collapseId = `dorkCollapse${idx}`;
    const preview = count === 0
      ? `<div class="small text-muted fst-italic">Sin resultados</div>`
      : `<ul class="list-unstyled mb-0">${results.slice(0,2).map(renderResultItem).join('')}</ul>`;

    return `
      <div class="card shadow-sm">
        <div class="card-body p-2">
          <div class="d-flex">
            <div class="flex-grow-1 me-2" style="min-width:0;">
              <div class="fw-semibold text-truncate" title="${escapeHTML(dork.description || '')}">${escapeHTML(dork.description || '')}</div>
              <div class="small text-muted text-truncate" title="${escapeHTML(dork.query || '')}">
                <code style="white-space:nowrap; max-width:100%; display:inline-block;">${escapeHTML(dork.query || '')}</code>
              </div>
              <div class="mt-2">${preview}</div>
            </div>

            <div class="text-end ms-2" style="min-width:8rem;">
              <div class="small text-muted mb-1">${count} resultado(s)</div>

              <div class="btn-group" role="group" aria-label="acciones">
                <button type="button" class="btn btn-sm btn-outline-secondary copy-btn" data-query="${escapeHTML(dork.query || '')}" title="Copiar query">Copiar</button>
                <button type="button" class="btn btn-sm btn-outline-primary view-btn" data-target="#${collapseId}" aria-expanded="false">Ver</button>
                <button type="button" class="btn btn-sm btn-outline-success open-btn" ${count === 0 ? 'disabled' : ''} title="Abrir hasta 5 enlaces">Abrir</button>
              </div>
            </div>
          </div>

          <div class="collapse mt-2" id="${collapseId}">
            <div class="card card-body p-2">
              <div class="mb-2 small text-muted">Resultados (mostrar hasta 100)</div>
              <div style="max-height:240px; overflow:auto;">
                <ul class="result-list list-unstyled mb-0">
                  ${results.map(renderResultItem).join('') || '<li class="small text-muted">Sin resultados</li>'}
                </ul>
              </div>
            </div>
          </div>

        </div>
      </div>
    `;
  }

  function bindCardEvents(cardEl, dork) {
    // copiar query
    qsa('.copy-btn', cardEl).forEach(btn => {
      btn.addEventListener('click', async () => {
        const q = btn.getAttribute('data-query') || '';
        try {
          await navigator.clipboard.writeText(q);
          const old = btn.innerHTML;
          btn.innerHTML = 'Copiado';
          setTimeout(() => btn.innerHTML = old, 1000);
        } catch (e) {
          console.error('copy failed', e);
        }
      });
    });

    // ver / colapsar (usa clase 'show' de bootstrap collapse para compatibilidad visual)
    qsa('.view-btn', cardEl).forEach(btn => {
      btn.addEventListener('click', () => {
        const target = btn.getAttribute('data-target');
        const el = target ? document.querySelector(target) : null;
        if (!el) return;
        // toggle clase 'show' para bootstrap collapse CSS
        el.classList.toggle('show');
      });
    });

    // abrir enlaces (hasta 5)
    const openBtn = cardEl.querySelector('.open-btn');
    if (openBtn) {
      openBtn.addEventListener('click', () => {
        const links = (dork.results || []).slice(0, 5).map(r => r.link).filter(Boolean);
        if (links.length === 0) return;
        if (links.length > 3) {
          if (!confirm(`Se abrirán ${links.length} pestañas (máx 5). ¿Continuar?`)) return;
        }
        links.forEach(u => window.open(u, '_blank', 'noopener'));
      });
    }
  }

  function renderAll(container, dataArray) {
    const list = container.querySelector('#dorksList');
    const summary = container.querySelector('#dorksSummary');
    const empty = container.querySelector('#dorksEmpty');

    if (!Array.isArray(dataArray) || dataArray.length === 0) {
      if (list) list.innerHTML = '';
      if (empty) empty.classList.remove('d-none');
      if (summary) summary.textContent = '0 dorks';
      return;
    }

    if (empty) empty.classList.add('d-none');

    // ordenar por cantidad de resultados (desc) para priorizar visualmente
    dataArray.sort((a,b) => (b.results?.length || 0) - (a.results?.length || 0));

    // render cards
    list.innerHTML = dataArray.map((d, i) => createCardHTML(d, i)).join('');
    if (summary) summary.textContent = `${dataArray.length} dorks — ${dataArray.filter(d => (d.results||[]).length>0).length} con resultados`;

    // bind events per card
    const cards = list.querySelectorAll('.card');
    cards.forEach((cardEl, idx) => {
      const dork = dataArray[idx];
      bindCardEvents(cardEl, dork);
    });
  }

  function initGraficosDorks(datos) {
    try {
      console.log('(desde dorks.js) Datos recibidos para Dorks:', datos);

      // Normalizar entrada:
      // - Si datos es array => se usa directamente
      // - Si datos.results existe => usar datos.results (compatibilidad)
      let dorksArray = [];
      if (Array.isArray(datos)) {
        dorksArray = datos;
      } else if (Array.isArray(datos && datos.results)) {
        dorksArray = datos.results;
      } else if (Array.isArray(datos && datos.dorks)) {
        dorksArray = datos.dorks;
      } else {
        console.warn('Datos de dorks no contienen un array reconocible. Se aborta render.');
        return;
      }

      // Cada dork esperado: { description, query, results:[{title,snippet,link}] }
      // Render en el DOM
      const container = document.getElementById('dorksModule');
      if (!container) throw new Error('Contenedor #dorksModule no encontrado en el DOM.');
      renderAll(container, dorksArray);

    } catch (err) {
      console.error('Error al renderizar Dorks:', err);
      const container = document.querySelector('.container-errores');
      if (container) {
        container.innerHTML = `<strong class="font-bold">Error:</strong>
          <span class="block sm:inline">⚠️ Error al renderizar datos: ${escapeHTML(err.message)}</span>`;
        container.classList.remove('hidden');
      }
    }
  }

  // registrar en window.Visuals (mismo patrón que dns.js)
  window.Visuals = window.Visuals || {};
  window.Visuals['dorks'] = initGraficosDorks;

})();
