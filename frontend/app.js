/* PluginDB — Single-page frontend (vanilla JS, hash-based routing) */
(function () {
  'use strict';

  // ---- CONFIG ----
  const CONFIG = { API_BASE: '/api/v1', ITEMS_PER_PAGE: 24, DEBOUNCE_MS: 200 };

  // ---- API CLIENT ----
  const API = {
    async get(path, params) {
      const url = new URL(CONFIG.API_BASE + path, location.origin);
      if (params) Object.entries(params).forEach(([k, v]) => {
        if (v !== null && v !== undefined && v !== '') url.searchParams.set(k, v);
      });
      const res = await fetch(url);
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `API error ${res.status}`);
      }
      return res.json();
    }
  };

  // ---- UTILITIES ----
  const _e = document.createElement('textarea');
  function escapeHtml(s) {
    if (s == null) return '';
    _e.textContent = String(s);
    return _e.innerHTML;
  }

  function debounce(fn, ms) {
    let t;
    return function () {
      clearTimeout(t);
      t = setTimeout(() => fn.apply(this, arguments), ms);
    };
  }

  function formatTags(tags, limit) {
    if (!tags || !tags.length) return '';
    const show = limit ? tags.slice(0, limit) : tags;
    return show.map(t =>
      `<a href="#/?tag=${encodeURIComponent(t)}" class="tag-pill">${escapeHtml(t)}</a>`
    ).join('');
  }

  function formatBadge(text, cls) {
    return `<span class="badge ${escapeHtml(cls || '')}">${escapeHtml(text)}</span>`;
  }

  function formatPriceBadge(pt) {
    const cls = { free: 'badge-green', freemium: 'badge-teal', paid: 'badge-blue', subscription: 'badge-purple' };
    return `<span class="badge ${cls[pt] || 'badge-default'}">${escapeHtml(pt)}</span>`;
  }

  function renderPagination(pg, baseHash) {
    if (!pg || pg.pages <= 1) return '';
    const sep = baseHash.includes('?') ? '&' : '?';
    const link = (p, label, disabled) =>
      disabled ? `<span class="page-link disabled">${label}</span>`
               : `<a href="${baseHash}${sep}page=${p}" class="page-link">${label}</a>`;
    let html = '<nav class="pagination" aria-label="Pagination">';
    html += link(pg.page - 1, '&laquo; Prev', pg.page <= 1);
    const start = Math.max(1, pg.page - 2);
    const end = Math.min(pg.pages, pg.page + 2);
    if (start > 1) { html += link(1, '1'); if (start > 2) html += '<span class="page-ellipsis">&hellip;</span>'; }
    for (let i = start; i <= end; i++) html += `<a href="${baseHash}${sep}page=${i}" class="page-link${i === pg.page ? ' active' : ''}">${i}</a>`;
    if (end < pg.pages) { if (end < pg.pages - 1) html += '<span class="page-ellipsis">&hellip;</span>'; html += link(pg.pages, pg.pages); }
    html += link(pg.page + 1, 'Next &raquo;', pg.page >= pg.pages);
    html += '</nav>';
    return html;
  }

  // ---- STATE HELPERS ----
  function showLoading(el) { el.innerHTML = '<div class="loading-spinner" aria-label="Loading"></div>'; }
  function showError(el, msg) {
    el.innerHTML = `<div class="state-error"><p>${escapeHtml(msg)}</p><button class="btn btn-retry">Retry</button></div>`;
    el.querySelector('.btn-retry').addEventListener('click', () => router());
  }
  function showEmpty(el, msg) { el.innerHTML = `<div class="state-empty"><p>${escapeHtml(msg || 'Nothing found.')}</p></div>`; }

  // ---- SHARED RENDERERS ----
  function pluginCard(p) {
    const mfr = p.manufacturer || {};
    return `<a href="#/plugins/${escapeHtml(p.slug)}" class="plugin-card">
      <div class="card-header"><span class="card-category">${escapeHtml(p.category)}</span>${formatPriceBadge(p.price_type)}</div>
      <h3 class="card-title">${escapeHtml(p.name)}</h3>
      <p class="card-mfr">${escapeHtml(mfr.name || '')}</p>
      <p class="card-desc">${escapeHtml((p.description || '').slice(0, 120))}${(p.description || '').length > 120 ? '&hellip;' : ''}</p>
      <div class="card-footer">${(p.formats || []).map(f => formatBadge(f, 'badge-sm')).join('')}</div>
    </a>`;
  }

  function pluginGrid(plugins) {
    return `<div class="plugin-grid">${plugins.map(pluginCard).join('')}</div>`;
  }

  // Build a baseHash for pagination that strips the page param from current params
  function baseHashWithout(params, key) {
    const copy = new URLSearchParams(params);
    copy.delete(key);
    const qs = copy.toString();
    return qs ? '#/?' + qs : '#/';
  }

  // ---- CACHED META ----
  let _categories = null;
  let _formats = null;
  let _osList = null;
  async function getCategories() { if (!_categories) _categories = await API.get('/categories'); return _categories; }
  async function getFormats() { if (!_formats) _formats = await API.get('/formats'); return _formats; }
  async function getOS() { if (!_osList) _osList = await API.get('/os'); return _osList; }

  // ---- VIEWS ----
  const Views = {};

  // == HOME / BROWSE ==
  Views.home = async function (params) {
    const app = document.getElementById('app');
    const q = params.get('q') || '';
    const category = params.get('category') || '';
    const subcategory = params.get('subcategory') || '';
    const format = params.get('format') || '';
    const os = params.get('os') || '';
    const priceType = params.get('price_type') || '';
    const tag = params.get('tag') || '';
    const yearMin = params.get('year_min') || '';
    const yearMax = params.get('year_max') || '';
    const sort = params.get('sort') || '';
    const order = params.get('order') || '';
    const page = parseInt(params.get('page'), 10) || 1;
    const hasFilters = category || subcategory || format || os || priceType || tag || yearMin || yearMax;

    // Fetch meta in parallel
    const [catData, fmtData, osData] = await Promise.all([getCategories(), getFormats(), getOS()]);
    const subcats = (category && catData.subcategories[category]) || [];

    // Build sort value string
    const sortVal = sort ? `${sort}_${order || 'asc'}` : '';

    // Render shell
    app.innerHTML = `
      <section class="hero">
        <h1>Discover Audio Plugins</h1>
        <div class="search-wrap">
          <input id="search-input" type="search" class="search-input" placeholder="Search plugins\u2026" value="${escapeHtml(q)}" autocomplete="off" aria-label="Search plugins">
          <div id="suggest-dropdown" class="suggest-dropdown hidden"></div>
          <button id="btn-random" class="btn btn-accent" title="Random plugin">Discover</button>
        </div>
      </section>
      <section class="browse-section">
        <div class="filter-bar">
          <select id="f-category" aria-label="Category"><option value="">All categories</option>${catData.categories.map(c => `<option value="${escapeHtml(c)}"${c === category ? ' selected' : ''}>${escapeHtml(c)}</option>`).join('')}</select>
          <select id="f-subcategory" aria-label="Subcategory"><option value="">All subcategories</option>${subcats.map(s => `<option value="${escapeHtml(s)}"${s === subcategory ? ' selected' : ''}>${escapeHtml(s)}</option>`).join('')}</select>
          <select id="f-format" aria-label="Format"><option value="">All formats</option>${Object.keys(fmtData.formats).map(f => `<option value="${escapeHtml(f)}"${f === format ? ' selected' : ''}>${escapeHtml(f)}</option>`).join('')}</select>
          <select id="f-os" aria-label="OS"><option value="">All OS</option>${Object.keys(osData.os).map(o => `<option value="${escapeHtml(o)}"${o === os ? ' selected' : ''}>${escapeHtml(o)}</option>`).join('')}</select>
          <select id="f-price" aria-label="Price type"><option value="">All prices</option>${['free','freemium','paid','subscription'].map(p => `<option value="${escapeHtml(p)}"${p === priceType ? ' selected' : ''}>${escapeHtml(p)}</option>`).join('')}</select>
          <input id="f-year-min" type="number" class="input-year" placeholder="Year from" value="${escapeHtml(yearMin)}" aria-label="Year from">
          <input id="f-year-max" type="number" class="input-year" placeholder="Year to" value="${escapeHtml(yearMax)}" aria-label="Year to">
          <select id="f-sort" aria-label="Sort"><option value="">Relevance</option><option value="name_asc"${sortVal === 'name_asc' ? ' selected' : ''}>Name A-Z</option><option value="name_desc"${sortVal === 'name_desc' ? ' selected' : ''}>Name Z-A</option><option value="created_at_desc"${sortVal === 'created_at_desc' ? ' selected' : ''}>Newest</option><option value="created_at_asc"${sortVal === 'created_at_asc' ? ' selected' : ''}>Oldest</option></select>
        </div>
        <div id="active-filters"></div>
        <div id="related-tags"></div>
        <div id="results-area"><div class="loading-spinner" aria-label="Loading"></div></div>
        <div id="pagination-area"></div>
      </section>`;

    // Wire events
    const searchInput = document.getElementById('search-input');
    const dropdown = document.getElementById('suggest-dropdown');

    // Suggest typeahead
    const doSuggest = debounce(async function () {
      const val = searchInput.value.trim();
      if (val.length < 1) { dropdown.classList.add('hidden'); return; }
      try {
        const data = await API.get('/suggest', { q: val });
        if (!data.results || !data.results.length) { dropdown.classList.add('hidden'); return; }
        dropdown.innerHTML = data.results.map(r =>
          `<div class="suggest-item" data-slug="${escapeHtml(r.slug)}">
            <span class="suggest-name">${escapeHtml(r.name)}</span>
            <span class="suggest-meta">${escapeHtml(r.manufacturer_name)} &middot; ${escapeHtml(r.category)}</span>
          </div>`
        ).join('');
        dropdown.classList.remove('hidden');
      } catch (_) { dropdown.classList.add('hidden'); }
    }, CONFIG.DEBOUNCE_MS);

    searchInput.addEventListener('input', doSuggest);
    searchInput.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') { e.preventDefault(); dropdown.classList.add('hidden'); applyFilters(); }
    });
    dropdown.addEventListener('click', function (e) {
      const item = e.target.closest('.suggest-item');
      if (item) { location.hash = '#/plugins/' + item.dataset.slug; }
    });
    document.addEventListener('click', function handler(e) {
      if (!e.target.closest('.search-wrap')) dropdown.classList.add('hidden');
    });

    // Random
    document.getElementById('btn-random').addEventListener('click', async function () {
      try { const p = await API.get('/plugins/random'); location.hash = '#/plugins/' + p.slug; } catch (_) {}
    });

    // Filters
    function applyFilters() {
      const p = new URLSearchParams();
      const qv = searchInput.value.trim();
      if (qv) p.set('q', qv);
      const cv = document.getElementById('f-category').value; if (cv) p.set('category', cv);
      const sv = document.getElementById('f-subcategory').value; if (sv) p.set('subcategory', sv);
      const fv = document.getElementById('f-format').value; if (fv) p.set('format', fv);
      const ov = document.getElementById('f-os').value; if (ov) p.set('os', ov);
      const pv = document.getElementById('f-price').value; if (pv) p.set('price_type', pv);
      const ym = document.getElementById('f-year-min').value; if (ym) p.set('year_min', ym);
      const yx = document.getElementById('f-year-max').value; if (yx) p.set('year_max', yx);
      const srt = document.getElementById('f-sort').value;
      if (srt) { const [sf, so] = srt.split('_'); p.set('sort', sf); p.set('order', so); }
      const qs = p.toString();
      location.hash = qs ? '#/?' + qs : '#/';
    }

    ['f-category', 'f-subcategory', 'f-format', 'f-os', 'f-price', 'f-sort'].forEach(id => {
      document.getElementById(id).addEventListener('change', applyFilters);
    });

    // Update subcategory options when category changes
    document.getElementById('f-category').addEventListener('change', function () {
      const sel = this.value;
      const subSel = document.getElementById('f-subcategory');
      const subs = (sel && catData.subcategories[sel]) || [];
      subSel.innerHTML = '<option value="">All subcategories</option>' + subs.map(s => `<option value="${escapeHtml(s)}">${escapeHtml(s)}</option>`).join('');
    });

    ['f-year-min', 'f-year-max'].forEach(id => {
      document.getElementById(id).addEventListener('change', applyFilters);
    });

    // Active filter pills
    const af = document.getElementById('active-filters');
    const pills = [];
    if (tag) pills.push({ label: 'tag: ' + tag, key: 'tag' });
    if (category) pills.push({ label: category, key: 'category' });
    if (subcategory) pills.push({ label: subcategory, key: 'subcategory' });
    if (format) pills.push({ label: format, key: 'format' });
    if (os) pills.push({ label: os, key: 'os' });
    if (priceType) pills.push({ label: priceType, key: 'price_type' });
    if (yearMin) pills.push({ label: 'from ' + yearMin, key: 'year_min' });
    if (yearMax) pills.push({ label: 'to ' + yearMax, key: 'year_max' });
    if (pills.length) {
      af.innerHTML = '<div class="filter-pills">' + pills.map(p =>
        `<span class="filter-pill" data-key="${escapeHtml(p.key)}">${escapeHtml(p.label)} <button aria-label="Remove filter">&times;</button></span>`
      ).join('') + '<button class="btn btn-sm" id="clear-filters">Clear all</button></div>';
      af.addEventListener('click', function (e) {
        const pill = e.target.closest('.filter-pill');
        if (pill) { params.delete(pill.dataset.key); params.delete('page'); location.hash = '#/?' + params.toString(); return; }
        if (e.target.id === 'clear-filters') { location.hash = '#/'; }
      });
    }

    // Fetch results
    const resultsArea = document.getElementById('results-area');
    const paginationArea = document.getElementById('pagination-area');
    try {
      const apiParams = { page, per_page: CONFIG.ITEMS_PER_PAGE };
      if (category) apiParams.category = category;
      if (subcategory) apiParams.subcategory = subcategory;
      if (format) apiParams.format = format;
      if (os) apiParams.os = os;
      if (priceType) apiParams.price_type = priceType;
      if (tag) apiParams.tag = tag;
      if (yearMin) apiParams.year_min = yearMin;
      if (yearMax) apiParams.year_max = yearMax;
      if (sort) apiParams.sort = sort;
      if (order) apiParams.order = order;

      let data;
      if (q) {
        apiParams.q = q;
        data = await API.get('/search', apiParams);
      } else {
        data = await API.get('/plugins', apiParams);
      }

      if (!data.data || !data.data.length) { showEmpty(resultsArea, 'No plugins found. Try adjusting your filters.'); }
      else {
        resultsArea.innerHTML = `<p class="results-count">${data.total} plugin${data.total !== 1 ? 's' : ''} found</p>` + pluginGrid(data.data);
        paginationArea.innerHTML = renderPagination(data.pagination, baseHashWithout(params, 'page'));
      }

      // Related tags
      if (data.related_tags && Object.keys(data.related_tags).length) {
        const rt = document.getElementById('related-tags');
        rt.innerHTML = '<div class="related-tags"><span class="related-label">Related tags:</span> ' +
          Object.entries(data.related_tags).slice(0, 8).map(([t]) =>
            `<a href="#/?tag=${encodeURIComponent(t)}" class="tag-pill tag-pill-sm">${escapeHtml(t)}</a>`
          ).join('') + '</div>';
      }
    } catch (err) { showError(resultsArea, err.message); }
  };

  // == PLUGIN DETAIL ==
  Views.pluginDetail = async function (slug) {
    const app = document.getElementById('app');
    showLoading(app);
    try {
      const p = await API.get(`/plugins/by-slug/${encodeURIComponent(slug)}`, { include: 'manufacturer_plugins' });
      const mfr = p.manufacturer || {};
      const fmtBadges = (p.formats || []).map(f => formatBadge(f, 'badge-format')).join('');
      const osBadges = (p.os || []).map(o => formatBadge(o, 'badge-os')).join('');
      const dawList = (p.daws || []).map(d => escapeHtml(d)).join(', ');
      const aliases = (p.aliases || []).map(a => escapeHtml(a)).join(', ');

      let html = `
        <nav class="breadcrumb"><a href="#/">Plugins</a> <span>&rsaquo;</span> <span>${escapeHtml(p.name)}</span></nav>
        <section class="detail-header">
          <h1>${escapeHtml(p.name)}</h1>
          <p class="detail-mfr">by <a href="#/manufacturers/${escapeHtml(mfr.slug)}">${escapeHtml(mfr.name)}</a></p>
          ${p.description ? `<p class="detail-desc">${escapeHtml(p.description)}</p>` : ''}
        </section>
        <section class="detail-meta">
          <div class="meta-grid">
            <div class="meta-item"><span class="meta-label">Category</span><span>${escapeHtml(p.category)}${p.subcategory ? ' / ' + escapeHtml(p.subcategory) : ''}</span></div>
            ${(p.formats || []).length ? `<div class="meta-item"><span class="meta-label">Formats</span><span>${fmtBadges}</span></div>` : ''}
            ${(p.os || []).length ? `<div class="meta-item"><span class="meta-label">OS</span><span>${osBadges}</span></div>` : ''}
            ${dawList ? `<div class="meta-item"><span class="meta-label">DAWs</span><span>${dawList}</span></div>` : ''}
            <div class="meta-item"><span class="meta-label">Price</span><span>${formatPriceBadge(p.price_type)}</span></div>
            ${p.year ? `<div class="meta-item"><span class="meta-label">Year</span><span>${escapeHtml(p.year)}</span></div>` : ''}
            ${aliases ? `<div class="meta-item"><span class="meta-label">Also known as</span><span>${aliases}</span></div>` : ''}
          </div>
        </section>`;

      if ((p.tags || []).length) {
        html += `<section class="detail-tags"><span class="meta-label">Tags</span><div class="tags-wrap">${formatTags(p.tags)}</div></section>`;
      }

      if (p.website) {
        html += `<section class="detail-links"><a href="${escapeHtml(p.website)}" class="btn btn-primary" target="_blank" rel="noopener">Visit website &rarr;</a></section>`;
      }

      // Manufacturer plugins
      if (p.manufacturer_plugins && p.manufacturer_plugins.length) {
        html += `<section class="detail-section"><h2>More from ${escapeHtml(mfr.name)}</h2>${pluginGrid(p.manufacturer_plugins)}</section>`;
      }

      html += '<section class="detail-section" id="similar-section"></section>';
      app.innerHTML = html;

      // Fetch similar plugins asynchronously
      if (p.id) {
        try {
          const sim = await API.get(`/plugins/${p.id}/similar`, { limit: 6 });
          if (sim.data && sim.data.length) {
            document.getElementById('similar-section').innerHTML = `<h2>Similar Plugins</h2>${pluginGrid(sim.data)}`;
          }
        } catch (_) { /* non-critical */ }
      }
    } catch (err) { showError(app, err.message); }
  };

  // == MANUFACTURER LIST ==
  Views.manufacturers = async function (params) {
    const app = document.getElementById('app');
    const search = params.get('search') || '';
    const sort = params.get('sort') || 'name';
    const order = params.get('order') || 'asc';
    const page = parseInt(params.get('page'), 10) || 1;

    app.innerHTML = `
      <section class="page-header"><h1>Manufacturers</h1></section>
      <section class="browse-section">
        <div class="filter-bar">
          <input id="mfr-search" type="search" class="search-input" placeholder="Search manufacturers\u2026" value="${escapeHtml(search)}" aria-label="Search manufacturers">
          <button id="mfr-sort" class="btn btn-sm">${sort === 'plugin_count' ? 'Most plugins' : 'A-Z'}</button>
        </div>
        <div id="results-area"><div class="loading-spinner" aria-label="Loading"></div></div>
        <div id="pagination-area"></div>
      </section>`;

    function buildHash(overrides) {
      const p = new URLSearchParams();
      const s = overrides.search !== undefined ? overrides.search : search;
      if (s) p.set('search', s);
      const srt = overrides.sort !== undefined ? overrides.sort : sort;
      const ord = overrides.order !== undefined ? overrides.order : order;
      if (srt !== 'name') { p.set('sort', srt); p.set('order', ord); }
      const qs = p.toString();
      return '#/manufacturers' + (qs ? '?' + qs : '');
    }

    document.getElementById('mfr-search').addEventListener('input', debounce(function () {
      location.hash = buildHash({ search: this.value.trim(), page: undefined });
    }, CONFIG.DEBOUNCE_MS));

    document.getElementById('mfr-sort').addEventListener('click', function () {
      const next = sort === 'plugin_count' ? 'name' : 'plugin_count';
      const nextOrd = next === 'plugin_count' ? 'desc' : 'asc';
      location.hash = buildHash({ sort: next, order: nextOrd });
    });

    const resultsArea = document.getElementById('results-area');
    const paginationArea = document.getElementById('pagination-area');
    try {
      const data = await API.get('/manufacturers', { search: search || undefined, sort, order, page, per_page: CONFIG.ITEMS_PER_PAGE });
      if (!data.data || !data.data.length) { showEmpty(resultsArea, 'No manufacturers found.'); return; }
      resultsArea.innerHTML = '<div class="mfr-grid">' + data.data.map(m =>
        `<a href="#/manufacturers/${escapeHtml(m.slug)}" class="mfr-card">
          <h3>${escapeHtml(m.name)}</h3>
          <p>${m.plugin_count} plugin${m.plugin_count !== 1 ? 's' : ''}</p>
          ${m.website ? `<span class="mfr-website">${escapeHtml(m.website.replace(/^https?:\/\//, ''))}</span>` : ''}
        </a>`
      ).join('') + '</div>';
      paginationArea.innerHTML = renderPagination(data.pagination, buildHash({}));
    } catch (err) { showError(resultsArea, err.message); }
  };

  // == MANUFACTURER DETAIL ==
  Views.manufacturerDetail = async function (slug, params) {
    const app = document.getElementById('app');
    showLoading(app);
    const page = parseInt(params.get('page'), 10) || 1;
    try {
      const data = await API.get(`/manufacturers/${encodeURIComponent(slug)}`, { page, per_page: CONFIG.ITEMS_PER_PAGE });
      const m = data.manufacturer;
      const catBadges = Object.entries(data.categories || {}).map(([c, n]) => formatBadge(`${c} (${n})`, 'badge-outline')).join('');

      let html = `
        <nav class="breadcrumb"><a href="#/manufacturers">Manufacturers</a> <span>&rsaquo;</span> <span>${escapeHtml(m.name)}</span></nav>
        <section class="detail-header">
          <h1>${escapeHtml(m.name)}</h1>
          <p>${data.plugin_count} plugin${data.plugin_count !== 1 ? 's' : ''}${m.website ? ` &middot; <a href="${escapeHtml(m.website)}" target="_blank" rel="noopener">${escapeHtml(m.website.replace(/^https?:\/\//, ''))}</a>` : ''}</p>
          ${catBadges ? `<div class="cat-badges">${catBadges}</div>` : ''}
        </section>`;

      if (data.plugins && data.plugins.length) {
        const bh = '#/manufacturers/' + encodeURIComponent(slug);
        html += `<section class="browse-section">${pluginGrid(data.plugins)}${renderPagination(data.pagination, bh)}</section>`;
      } else {
        html += '<section class="browse-section"><p>No plugins listed yet.</p></section>';
      }
      app.innerHTML = html;
    } catch (err) { showError(app, err.message); }
  };

  // ---- ROUTER ----
  function parseHash() {
    const raw = location.hash.replace(/^#/, '') || '/';
    const qIdx = raw.indexOf('?');
    const path = qIdx >= 0 ? raw.slice(0, qIdx) : raw;
    const qs = qIdx >= 0 ? raw.slice(qIdx + 1) : '';
    return { path: path || '/', params: new URLSearchParams(qs) };
  }

  function updateNav(route) {
    document.querySelectorAll('#main-nav .nav-link[data-route]').forEach(a => {
      a.classList.toggle('active', a.dataset.route === route);
    });
  }

  async function router() {
    const { path, params } = parseHash();
    window.scrollTo(0, 0);

    // #/plugins/:slug
    const pluginMatch = path.match(/^\/plugins\/(.+)$/);
    if (pluginMatch) { updateNav('home'); return Views.pluginDetail(decodeURIComponent(pluginMatch[1])); }

    // #/manufacturers/:slug
    const mfrMatch = path.match(/^\/manufacturers\/(.+)$/);
    if (mfrMatch) { updateNav('manufacturers'); return Views.manufacturerDetail(decodeURIComponent(mfrMatch[1]), params); }

    // #/manufacturers
    if (path === '/manufacturers') { updateNav('manufacturers'); return Views.manufacturers(params); }

    // default: home
    updateNav('home');
    return Views.home(params);
  }

  window.addEventListener('hashchange', router);
  router();
})();
