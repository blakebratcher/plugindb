/* PluginDB — Single-page frontend (vanilla JS, hash-based routing)
   LaunchBox-inspired: 20-cycle progressive refinement */
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
    html += link(pg.page - 1, 'Prev', pg.page <= 1);
    const start = Math.max(1, pg.page - 2);
    const end = Math.min(pg.pages, pg.page + 2);
    if (start > 1) { html += link(1, '1'); if (start > 2) html += '<span class="page-ellipsis">&hellip;</span>'; }
    for (let i = start; i <= end; i++) html += `<a href="${baseHash}${sep}page=${i}" class="page-link${i === pg.page ? ' active' : ''}">${i}</a>`;
    if (end < pg.pages) { if (end < pg.pages - 1) html += '<span class="page-ellipsis">&hellip;</span>'; html += link(pg.pages, pg.pages); }
    html += link(pg.page + 1, 'Next', pg.page >= pg.pages);
    html += '</nav>';
    return html;
  }

  // ---- STATE ----
  let viewMode = localStorage.getItem('plugindb_view') || 'grid';

  // ---- STATE HELPERS ----
  function showLoading(el) { el.innerHTML = '<div class="loading-spinner" aria-label="Loading"></div>'; }

  // Cycle 16: Better skeleton loaders
  function showSkeletonGrid(el, count) {
    const n = count || 6;
    const card = `<div class="skeleton-card">
      <div class="skeleton-card-image"></div>
      <div class="skeleton-card-body">
        <div class="skeleton-line"></div>
        <div class="skeleton-line"></div>
        <div class="skeleton-line"></div>
      </div>
    </div>`;
    el.innerHTML = '<div class="skeleton-grid">' + card.repeat(n) + '</div>';
  }

  function showError(el, msg) {
    el.innerHTML = `<div class="state-error"><p>${escapeHtml(msg)}</p><button class="btn btn-retry">Retry</button></div>`;
    el.querySelector('.btn-retry').addEventListener('click', () => router());
  }
  function showEmpty(el, msg) { el.innerHTML = `<div class="state-empty"><p>${escapeHtml(msg || 'Nothing found.')}</p></div>`; }

  function generatePlaceholder(name, category) {
    return '<div class="card-placeholder"></div>';
  }

  // Cycle 20: Lazy image loading with fade-in
  function onImgLoad(e) { e.target.classList.add('loaded'); }
  function wireImageLoading(root) {
    root.querySelectorAll('.card-image img, .pd-hero img').forEach(function(img) {
      if (img.complete) img.classList.add('loaded');
      else img.addEventListener('load', onImgLoad);
    });
  }

  // ---- SHARED RENDERERS ----
  function pluginCard(p) {
    const mfr = p.manufacturer || {};
    const placeholder = generatePlaceholder(p.name, p.category);
    const onerrorFallback = 'this.onerror=null;this.parentNode.innerHTML=decodeURIComponent(\'' + encodeURIComponent(placeholder) + '\')';
    const imageHtml = p.image_url
      ? `<div class="card-image"><img src="/api/v1/image-proxy?url=${encodeURIComponent(p.image_url)}" alt="${escapeHtml(p.name)}" loading="lazy" onerror="${escapeHtml(onerrorFallback)}"></div>`
      : `<div class="card-image">${placeholder}</div>`;
    return `<a href="#/plugins/${escapeHtml(p.slug)}" class="plugin-card">
      ${imageHtml}
      <div class="card-body">
        <div class="card-header"><span class="card-category">${escapeHtml(p.category)}${p.subcategory ? ' / ' + escapeHtml(p.subcategory) : ''}</span></div>
        <h3 class="card-title">${escapeHtml(p.name)}</h3>
        <p class="card-mfr">${escapeHtml(mfr.name || '')}${p.year ? ' \u00B7 ' + escapeHtml(p.year) : ''}</p>
      </div>
    </a>`;
  }

  function pluginGrid(plugins, extraClass) {
    const cls = 'plugin-grid' + (extraClass ? ' ' + extraClass : '') + (viewMode === 'list' ? ' list-view' : '');
    return `<div class="${cls}">${plugins.map(pluginCard).join('')}</div>`;
  }

  // Cycle 13: Carousel for similar/related
  function pluginCarousel(plugins) {
    return `<div class="pd-carousel">${plugins.map(pluginCard).join('')}</div>`;
  }

  // Cycle 3: View toggle HTML
  function viewToggleHtml() {
    return `<div class="view-toggle">
      <button class="view-btn${viewMode === 'grid' ? ' active' : ''}" data-view="grid" title="Grid view" aria-label="Grid view">
        <svg viewBox="0 0 16 16" fill="currentColor"><rect x="1" y="1" width="6" height="6" rx="1"/><rect x="9" y="1" width="6" height="6" rx="1"/><rect x="1" y="9" width="6" height="6" rx="1"/><rect x="9" y="9" width="6" height="6" rx="1"/></svg>
      </button>
      <button class="view-btn${viewMode === 'list' ? ' active' : ''}" data-view="list" title="List view" aria-label="List view">
        <svg viewBox="0 0 16 16" fill="currentColor"><rect x="1" y="1" width="14" height="3" rx="1"/><rect x="1" y="6" width="14" height="3" rx="1"/><rect x="1" y="11" width="14" height="3" rx="1"/></svg>
      </button>
    </div>`;
  }

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
  let _stats = null;
  async function getCategories() { if (!_categories) _categories = await API.get('/categories'); return _categories; }
  async function getFormats() { if (!_formats) _formats = await API.get('/formats'); return _formats; }
  async function getOS() { if (!_osList) _osList = await API.get('/os'); return _osList; }
  async function getStats() { if (!_stats) _stats = await API.get('/stats'); return _stats; }

  // ---- CYCLE 11: Info row icons ----
  const INFO_ICONS = {
    Category:   '<svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor"><path d="M1 3.5A1.5 1.5 0 012.5 2h3.879a1.5 1.5 0 011.06.44l1.122 1.12A1.5 1.5 0 009.62 4H13.5A1.5 1.5 0 0115 5.5v7a1.5 1.5 0 01-1.5 1.5h-11A1.5 1.5 0 011 12.5v-9z"/></svg>',
    Formats:    '<svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor"><path d="M4 1h8a2 2 0 012 2v10a2 2 0 01-2 2H4a2 2 0 01-2-2V3a2 2 0 012-2zm0 1.5a.5.5 0 00-.5.5v10a.5.5 0 00.5.5h8a.5.5 0 00.5-.5V3a.5.5 0 00-.5-.5H4z"/></svg>',
    'Operating Systems': '<svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor"><path d="M2 3a1 1 0 011-1h10a1 1 0 011 1v8a1 1 0 01-1 1H3a1 1 0 01-1-1V3zm1 1v6h10V4H3zm0 9v1h10v-1H3z"/></svg>',
    Price:      '<svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor"><circle cx="8" cy="8" r="7" fill="none" stroke="currentColor" stroke-width="1.5"/><text x="8" y="11" text-anchor="middle" font-size="9" fill="currentColor">$</text></svg>',
    'Release Year': '<svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor"><path d="M4.5 1a.5.5 0 01.5.5V2h6v-.5a.5.5 0 011 0V2h1.5A1.5 1.5 0 0115 3.5v10a1.5 1.5 0 01-1.5 1.5h-11A1.5 1.5 0 011 13.5v-10A1.5 1.5 0 012.5 2H4v-.5a.5.5 0 01.5-.5zM2.5 6v7.5h11V6h-11z"/></svg>',
    Developer:  '<svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor"><path d="M8 8a3 3 0 100-6 3 3 0 000 6zm-5 6s-1 0-1-1 1-4 6-4 6 3 6 4-1 1-1 1H3z"/></svg>',
    'DAW Compatibility': '<svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor"><path d="M6 1v3H1V1h5zm9 0v3h-5V1h5zM6 6v3H1V6h5zm9 0v3h-5V6h5zM6 11v3H1v-3h5zm9 0v3h-5v-3h5z"/></svg>',
    'Alternate Names': '<svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor"><path d="M2 2v12h12V2H2zm1 1h4v4H3V3zm0 5h4v4H3V8zm5-5h4v4H8V3zm0 5h4v4H8V8z"/></svg>'
  };

  // ---- VIEWS ----
  const Views = {};

  // == HOME / BROWSE ==
  Views.home = async function (params) {
    document.title = 'PluginDB - The Plugin Database';
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
    const [catData, fmtData, osData, statsData] = await Promise.all([getCategories(), getFormats(), getOS(), getStats()]);
    const subcats = (category && catData.subcategories[category]) || [];

    const sortVal = sort ? `${sort}_${order || 'asc'}` : '';

    // Cycle 7: Category pills (no counts — cleaner)
    const catPillsHtml = catData.categories.map(c => {
      const active = c === category ? ' active' : '';
      return `<button class="cat-pill${active}" data-cat="${escapeHtml(c)}">${escapeHtml(c)}</button>`;
    }).join('');

    // Clear all link if any filter is active
    const clearAllHtml = hasFilters ? `<button class="btn-clear-filters" id="btn-clear-all-filters">Clear all</button>` : '';

    // Render shell — compact, content-first layout
    app.innerHTML = `
      <section class="hero" id="hero-section">
        <div class="hero-title-row">
          <h1>The Plugin Database</h1>
          <div class="hero-stats-inline">
            <span class="hero-stat-inline"><strong>${statsData.total_plugins || 0}</strong> plugins</span>
            <span class="hero-stat-inline"><strong>${statsData.total_manufacturers || 0}</strong> manufacturers</span>
          </div>
        </div>
        <div class="search-wrap">
          <div class="search-input-wrap">
            <svg class="search-icon" viewBox="0 0 16 16" fill="currentColor"><path d="M11.742 10.344a6.5 6.5 0 10-1.397 1.398h-.001l3.85 3.85a1 1 0 001.415-1.414l-3.85-3.85-.017.016zm-5.242.156a5 5 0 110-10 5 5 0 010 10z"/></svg>
            <input id="search-input" type="search" class="search-input" placeholder="Search plugins\u2026" value="${escapeHtml(q)}" autocomplete="off" aria-label="Search plugins">
            <button id="search-clear" class="search-clear${q ? ' visible' : ''}" aria-label="Clear search" type="button">&times;</button>
            <button id="btn-random" class="btn-random-inline" title="Random plugin" type="button">\uD83C\uDFB2</button>
            <span class="search-shortcut">/</span>
            <div id="suggest-dropdown" class="suggest-dropdown hidden"></div>
          </div>
        </div>
      </section>
      <section class="browse-section">
        ${q ? `<div class="search-active-banner" id="search-active-banner"><span class="search-query-text">Showing results for <strong>'${escapeHtml(q)}'</strong></span><button class="btn-clear-search" id="btn-clear-search">Clear search</button></div>` : ''}
        <div class="category-filter-bar" id="filter-bar">
          <div class="cat-pills-group">
            <button class="cat-pill${!category ? ' active' : ''}" data-cat="">All</button>
            ${catPillsHtml}
          </div>
          <div class="filter-dropdowns-group">
            <select id="f-subcategory" aria-label="Subcategory"><option value="">All subcategories</option>${subcats.map(s => `<option value="${escapeHtml(s)}"${s === subcategory ? ' selected' : ''}>${escapeHtml(s)}</option>`).join('')}</select>
            <select id="f-format" aria-label="Format"><option value="">All formats</option>${Object.keys(fmtData.formats).map(f => `<option value="${escapeHtml(f)}"${f === format ? ' selected' : ''}>${escapeHtml(f)}</option>`).join('')}</select>
            <select id="f-os" aria-label="OS"><option value="">All OS</option>${Object.keys(osData.os).map(o => `<option value="${escapeHtml(o)}"${o === os ? ' selected' : ''}>${escapeHtml(o)}</option>`).join('')}</select>
            <select id="f-price" aria-label="Price type"><option value="">All prices</option>${['free','paid','freemium'].map(p => `<option value="${escapeHtml(p)}"${p === priceType ? ' selected' : ''}>${escapeHtml(p)}</option>`).join('')}</select>
            <div class="year-range">
              <input id="f-year-min" type="number" class="input-year" placeholder="From" value="${escapeHtml(yearMin)}" aria-label="Year from">
              <span class="year-range-sep">&ndash;</span>
              <input id="f-year-max" type="number" class="input-year" placeholder="To" value="${escapeHtml(yearMax)}" aria-label="Year to">
            </div>
            ${clearAllHtml}
          </div>
        </div>
        <div id="active-filters"></div>
        <div id="related-tags"></div>
        <div id="results-toolbar"></div>
        <div id="results-area"><div class="loading-spinner" aria-label="Loading"></div></div>
        <div id="pagination-area"></div>
      </section>`;

    // Wire events
    const searchInput = document.getElementById('search-input');
    const dropdown = document.getElementById('suggest-dropdown');

    // Header compact search — show/hide based on scroll past hero
    var heroSection = document.getElementById('hero-section');
    var headerSearch = document.getElementById('header-search');
    if (heroSection && headerSearch) {
      var headerSearchInput = headerSearch.querySelector('.header-search-input');
      var headerSearchClear = headerSearch.querySelector('.header-search-clear');
      // Sync initial value
      if (headerSearchInput) headerSearchInput.value = q;

      var _heroObserver = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
          if (entry.isIntersecting) {
            headerSearch.classList.remove('visible');
          } else {
            headerSearch.classList.add('visible');
          }
        });
      }, { threshold: 0, rootMargin: '-48px 0px 0px 0px' });
      _heroObserver.observe(heroSection);

      // Wire header search input
      if (headerSearchInput) {
        headerSearchInput.addEventListener('keydown', function(e) {
          if (e.key === 'Enter') {
            e.preventDefault();
            var val = headerSearchInput.value.trim();
            var p = new URLSearchParams(params);
            p.delete('page');
            if (val) p.set('q', val); else p.delete('q');
            var qs = p.toString();
            location.hash = qs ? '#/?' + qs : '#/';
          }
        });
        headerSearchInput.addEventListener('input', function() {
          if (headerSearchClear) headerSearchClear.classList.toggle('visible', headerSearchInput.value.length > 0);
        });
      }
      if (headerSearchClear) {
        headerSearchClear.addEventListener('click', function() {
          if (headerSearchInput) headerSearchInput.value = '';
          this.classList.remove('visible');
          if (params.get('q')) { params.delete('q'); params.delete('page'); location.hash = '#/?' + params.toString(); }
          if (headerSearchInput) headerSearchInput.focus();
        });
      }
    }

    // Wire clear search banner
    var clearSearchBtn = document.getElementById('btn-clear-search');
    if (clearSearchBtn) {
      clearSearchBtn.addEventListener('click', function() {
        var p = new URLSearchParams(params);
        p.delete('q');
        p.delete('page');
        var qs = p.toString();
        location.hash = qs ? '#/?' + qs : '#/';
      });
    }

    // Wire clear all filters button in filter bar
    var clearAllBtn = document.getElementById('btn-clear-all-filters');
    if (clearAllBtn) {
      clearAllBtn.addEventListener('click', function() {
        if (q) location.hash = '#/?q=' + encodeURIComponent(q);
        else location.hash = '#/';
      });
    }

    // Suggest typeahead
    const doSuggest = debounce(async function () {
      const val = searchInput.value.trim();
      if (val.length < 1) { dropdown.classList.add('hidden'); return; }
      try {
        const data = await API.get('/suggest', { q: val });
        if (!data.results || !data.results.length) { dropdown.classList.add('hidden'); return; }
        dropdown.innerHTML = data.results.map(r =>
          `<div class="suggest-item" data-slug="${escapeHtml(r.slug)}">
            ${r.image_url ? `<img class="suggest-thumb" src="/api/v1/image-proxy?url=${encodeURIComponent(r.image_url)}" alt="" loading="lazy" onerror="this.style.display='none'">` : ''}
            <span class="suggest-name">${escapeHtml(r.name)}</span>
            <span class="suggest-meta">${escapeHtml(r.manufacturer_name)} &middot; ${escapeHtml(r.category)}</span>
          </div>`
        ).join('');
        dropdown.classList.remove('hidden');
      } catch (_) { dropdown.classList.add('hidden'); }
    }, CONFIG.DEBOUNCE_MS);

    searchInput.addEventListener('input', function() {
      var cb = document.getElementById('search-clear');
      if (cb) cb.classList.toggle('visible', searchInput.value.length > 0);
      doSuggest();
    });
    document.getElementById('search-clear').addEventListener('click', function() {
      searchInput.value = '';
      this.classList.remove('visible');
      dropdown.classList.add('hidden');
      if (params.get('q')) { params.delete('q'); params.delete('page'); location.hash = '#/?' + params.toString(); }
      searchInput.focus();
    });
    let suggestIdx = -1;
    searchInput.addEventListener('keydown', function (e) {
      const items = dropdown.querySelectorAll('.suggest-item');
      if (e.key === 'ArrowDown' && items.length) {
        e.preventDefault();
        suggestIdx = Math.min(suggestIdx + 1, items.length - 1);
        items.forEach((it, i) => it.classList.toggle('suggest-item-active', i === suggestIdx));
      } else if (e.key === 'ArrowUp' && items.length) {
        e.preventDefault();
        suggestIdx = Math.max(suggestIdx - 1, 0);
        items.forEach((it, i) => it.classList.toggle('suggest-item-active', i === suggestIdx));
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (suggestIdx >= 0 && items[suggestIdx]) {
          location.hash = '#/plugins/' + items[suggestIdx].dataset.slug;
        } else {
          dropdown.classList.add('hidden');
          applyFilters();
        }
        suggestIdx = -1;
      } else if (e.key === 'Escape') {
        dropdown.classList.add('hidden');
        suggestIdx = -1;
      }
    });
    dropdown.addEventListener('click', function (e) {
      const item = e.target.closest('.suggest-item');
      if (item) { location.hash = '#/plugins/' + item.dataset.slug; }
    });

    // Random
    document.getElementById('btn-random').addEventListener('click', async function () {
      try { const p = await API.get('/plugins/random'); location.hash = '#/plugins/' + p.slug; } catch (_) {}
    });

    // Cycle 7: Category pill clicks
    document.querySelectorAll('.cat-pill').forEach(function(btn) {
      btn.addEventListener('click', function() {
        const cat = this.dataset.cat;
        const p = new URLSearchParams(params);
        p.delete('page');
        p.delete('subcategory');
        if (cat) p.set('category', cat);
        else p.delete('category');
        const qs = p.toString();
        location.hash = qs ? '#/?' + qs : '#/';
      });
    });

    // Filters
    function applyFilters() {
      const p = new URLSearchParams();
      const qv = searchInput.value.trim();
      if (qv) p.set('q', qv);
      // Keep current category from pills
      if (category) p.set('category', category);
      const sv = document.getElementById('f-subcategory').value; if (sv) p.set('subcategory', sv);
      const fv = document.getElementById('f-format').value; if (fv) p.set('format', fv);
      const ov = document.getElementById('f-os').value; if (ov) p.set('os', ov);
      const pv = document.getElementById('f-price').value; if (pv) p.set('price_type', pv);
      const ym = document.getElementById('f-year-min').value; if (ym) p.set('year_min', ym);
      const yx = document.getElementById('f-year-max').value; if (yx) p.set('year_max', yx);
      // Preserve current sort if set
      if (sort) p.set('sort', sort);
      if (order) p.set('order', order);
      const qs = p.toString();
      location.hash = qs ? '#/?' + qs : '#/';
    }

    ['f-subcategory', 'f-format', 'f-os', 'f-price'].forEach(id => {
      document.getElementById(id).addEventListener('change', applyFilters);
    });

    // Update subcategory options when category changes (via pills now)

    ['f-year-min', 'f-year-max'].forEach(id => {
      document.getElementById(id).addEventListener('change', applyFilters);
    });

    // Active filter pills
    const af = document.getElementById('active-filters');
    const pills = [];
    if (tag) pills.push({ label: 'tag: ' + tag, key: 'tag' });
    if (subcategory) pills.push({ label: subcategory, key: 'subcategory' });
    if (format) pills.push({ label: format, key: 'format' });
    if (os) pills.push({ label: os, key: 'os' });
    if (priceType) pills.push({ label: priceType, key: 'price_type' });
    if (yearMin) pills.push({ label: 'from ' + yearMin, key: 'year_min' });
    if (yearMax) pills.push({ label: 'to ' + yearMax, key: 'year_max' });
    if (pills.length) {
      af.innerHTML = '<div class="filter-pills">' + pills.map(p =>
        `<span class="filter-pill" data-key="${escapeHtml(p.key)}">${escapeHtml(p.label)} <button aria-label="Remove filter">&times;</button></span>`
      ).join('') + '</div>';
      af.addEventListener('click', function (e) {
        const pill = e.target.closest('.filter-pill');
        if (pill) { params.delete(pill.dataset.key); params.delete('page'); location.hash = '#/?' + params.toString(); }
      });
    }

    // Fetch results
    const resultsArea = document.getElementById('results-area');
    const paginationArea = document.getElementById('pagination-area');
    const toolbarArea = document.getElementById('results-toolbar');
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

      if (!data.data || !data.data.length) {
        toolbarArea.innerHTML = '';
        showEmpty(resultsArea, 'No plugins found. Try adjusting your filters.');
      } else {
        // Toolbar with count + sort dropdown + view toggle
        const sortDropdownHtml = `<select class="toolbar-sort" id="toolbar-sort" aria-label="Sort">
          <option value="">Sort by</option>
          <option value="name_asc"${sortVal === 'name_asc' ? ' selected' : ''}>Name A-Z</option>
          <option value="name_desc"${sortVal === 'name_desc' ? ' selected' : ''}>Name Z-A</option>
          <option value="year_desc"${sortVal === 'year_desc' ? ' selected' : ''}>Release Date (Newest)</option>
          <option value="year_asc"${sortVal === 'year_asc' ? ' selected' : ''}>Release Date (Oldest)</option>
          <option value="created_at_desc"${sortVal === 'created_at_desc' ? ' selected' : ''}>Recently Added</option>
        </select>`;
        toolbarArea.innerHTML = `<div class="results-toolbar">
          <span class="results-count">${data.total} plugin${data.total !== 1 ? 's' : ''}</span>
          <div class="toolbar-right">${sortDropdownHtml}${viewToggleHtml()}</div>
        </div>`;

        // Wire sort dropdown in toolbar
        document.getElementById('toolbar-sort').addEventListener('change', function() {
          var p = new URLSearchParams(params);
          p.delete('page');
          var srt = this.value;
          if (srt) {
            var lastUnderscore = srt.lastIndexOf('_');
            p.set('sort', srt.substring(0, lastUnderscore));
            p.set('order', srt.substring(lastUnderscore + 1));
          } else {
            p.delete('sort');
            p.delete('order');
          }
          var qs = p.toString();
          location.hash = qs ? '#/?' + qs : '#/';
        });

        // Wire view toggle
        toolbarArea.querySelectorAll('.view-btn').forEach(function(btn) {
          btn.addEventListener('click', function() {
            viewMode = this.dataset.view;
            localStorage.setItem('plugindb_view', viewMode);
            toolbarArea.querySelectorAll('.view-btn').forEach(b => b.classList.toggle('active', b.dataset.view === viewMode));
            const grid = resultsArea.querySelector('.plugin-grid');
            if (grid) grid.classList.toggle('list-view', viewMode === 'list');
          });
        });

        resultsArea.innerHTML = pluginGrid(data.data);
        wireImageLoading(resultsArea);
        paginationArea.innerHTML = renderPagination(data.pagination, baseHashWithout(params, 'page'));
      }

      // Related tags
      if (data.related_tags && Object.keys(data.related_tags).length) {
        const rt = document.getElementById('related-tags');
        rt.innerHTML = '<div class="related-tags"><span class="related-label">Related:</span> ' +
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
    document.title = 'Loading... - PluginDB';
    try {
      const p = await API.get(`/plugins/by-slug/${encodeURIComponent(slug)}`, { include: 'manufacturer_plugins' });
      const mfr = p.manufacturer || {};
      document.title = `${p.name} by ${mfr.name} - PluginDB`;

      const placeholder = generatePlaceholder(p.name, p.category);
      const onerrorFallback = 'this.onerror=null;this.parentNode.innerHTML=decodeURIComponent(\'' + encodeURIComponent(placeholder) + '\')';

      // Hero
      const heroHtml = p.image_url
        ? `<div class="pd-hero"><img src="/api/v1/image-proxy?url=${encodeURIComponent(p.image_url)}" alt="${escapeHtml(p.name)}" onerror="${escapeHtml(onerrorFallback)}"><div class="pd-hero-overlay"></div></div>`
        : `<div class="pd-hero pd-hero--empty"><div class="pd-hero-placeholder">${placeholder}</div><div class="pd-hero-overlay"></div></div>`;

      // Title bar — name, manufacturer, and description as subtitle
      const titleHtml = `
        <div class="pd-title-bar">
          <h1 class="pd-name">${escapeHtml(p.name)}</h1>
          <div class="pd-title-meta">
            <a href="#/manufacturers/${escapeHtml(mfr.slug)}" class="pd-mfr-link">${escapeHtml(mfr.name)}</a>
          </div>
          ${p.description ? `<p class="pd-subtitle">${escapeHtml(p.description)}</p>` : ''}
        </div>`;

      // Inline sections (LaunchBox-style: no tabs, all content visible)
      const hasTags = (p.tags || []).length > 0;
      const hasDesc = !!p.description;
      const hasMfrPlugins = p.manufacturer_plugins && p.manufacturer_plugins.length > 0;

      // Cycle 11: Info table with icons
      const infoRows = [
        ['Category', escapeHtml(p.category) + (p.subcategory ? ' / ' + escapeHtml(p.subcategory) : '')],
        ['Formats', (p.formats || []).map(f => formatBadge(f, 'badge-format')).join(' ')],
        ['Operating Systems', (p.os || []).map(o => formatBadge(o, 'badge-os')).join(' ')],
        ['Price', formatPriceBadge(p.price_type)],
        ['Release Year', p.year ? escapeHtml(p.year) : null],
      ].filter(r => r[1]).map(([label, value]) => {
        const icon = INFO_ICONS[label] || '';
        return `<div class="pd-info-row">${icon ? `<span class="pd-info-icon">${icon}</span>` : ''}<span class="pd-info-label">${label}</span><span class="pd-info-value">${value}</span></div>`;
      }).join('');

      // Inline sections
      const detailsSection = `<section class="pd-section">
        <h2 class="pd-section-title">Details</h2>
        <div class="pd-info-table">${infoRows}</div>
      </section>`;

      // Description is now in the title bar as a subtitle — no separate Overview section

      const tagsSection = hasTags ? `<section class="pd-section">
        <h2 class="pd-section-title">Tags</h2>
        <div class="pd-tags">${formatTags(p.tags)}</div>
      </section>` : '';

      // Resources section
      const resourceCards = [];
      if (p.website) {
        const websiteDomain = (function(url) { try { return new URL(url).hostname; } catch(_) { return url; } })(p.website);
        resourceCards.push(`<a href="${escapeHtml(p.website)}" class="resource-card" target="_blank" rel="noopener">
          <svg class="resource-card-icon" viewBox="0 0 16 16" width="18" height="18" fill="currentColor"><path d="M8 0a8 8 0 100 16A8 8 0 008 0zm-.5 1.07A6.97 6.97 0 001.05 7H4.1a18 18 0 01.4-4.43c.62-.22 1.28-.38 1.97-.46L7.5 1.07zM8.5 1.07l1.03 1.04c.69.08 1.35.24 1.97.46.26 1.35.38 2.86.4 4.43h3.05A6.97 6.97 0 008.5 1.07zM5.15 7a17 17 0 00-.05.5V8h5.8v-.5a17 17 0 00-.05-.5H5.15zm-1.05 0H1.05a6.97 6.97 0 006.45 7.93l-1.03-1.04c-.69-.08-1.35-.24-1.97-.46A17 17 0 014.1 9zm7.8 0a17 17 0 01-.4 4.43c-.62.22-1.28.38-1.97.46l-1.03 1.04A6.97 6.97 0 0014.95 9H11.9z"/></svg>
          <div><div class="resource-card-name">Official Website</div><div class="resource-card-domain">${escapeHtml(websiteDomain)}</div></div>
        </a>`);
      }
      if (p.manual_url && p.manual_url !== p.website) {
        const manualDomain = (function(url) { try { return new URL(url).hostname; } catch(_) { return url; } })(p.manual_url);
        resourceCards.push(`<a href="${escapeHtml(p.manual_url)}" class="resource-card" target="_blank" rel="noopener">
          <svg class="resource-card-icon" viewBox="0 0 16 16" width="18" height="18" fill="currentColor"><path d="M1 2.828c.885-.37 2.154-.769 3.388-.893C5.632 1.785 6.937 1.92 8 2.702c1.063-.782 2.368-.917 3.612-.767 1.234.124 2.503.523 3.388.893v9.923c-.918-.35-2.107-.692-3.287-.81-1.188-.119-2.39-.023-3.413.56v.001c-.01.005-.022.009-.032.013-.005.002-.01.005-.017.007a.066.066 0 01-.048 0c-.007-.002-.012-.005-.017-.007a.148.148 0 01-.032-.013v-.001c-1.023-.583-2.225-.679-3.413-.56-1.18.118-2.37.46-3.287.81V2.828zM7.5 3.621C6.57 3.016 5.396 2.887 4.28 3.006c-.927.1-1.852.37-2.53.622v8.218c.748-.268 1.629-.508 2.53-.601 1.1-.114 2.204.01 3.22.543V3.62zm1 8.788c1.016-.533 2.12-.657 3.22-.543.9.093 1.782.333 2.53.6V3.63c-.678-.252-1.603-.522-2.53-.622-1.116-.12-2.29.01-3.22.615v8.787z"/></svg>
          <div><div class="resource-card-name">Documentation</div><div class="resource-card-domain">${escapeHtml(manualDomain)}</div></div>
        </a>`);
      }
      if (p.video_url) {
        const videoDomain = (function(url) { try { return new URL(url).hostname; } catch(_) { return url; } })(p.video_url);
        resourceCards.push(`<a href="${escapeHtml(p.video_url)}" class="resource-card" target="_blank" rel="noopener">
          <svg class="resource-card-icon" viewBox="0 0 16 16" width="18" height="18" fill="currentColor"><path d="M8 0a8 8 0 100 16A8 8 0 008 0zm-1.5 4.5l5 3.5-5 3.5v-7z"/></svg>
          <div><div class="resource-card-name">Watch Demo</div><div class="resource-card-domain">${escapeHtml(videoDomain)}</div></div>
        </a>`);
      }
      // Only show marketplace links for paid plugins (free ones usually aren't listed)
      if (p.price_type === 'paid' || p.price_type === 'freemium') {
        const kvrSlug = encodeURIComponent(p.slug);
        resourceCards.push(`<a href="https://www.kvraudio.com/product/${kvrSlug}" class="resource-card" target="_blank" rel="noopener">
          <svg class="resource-card-icon" viewBox="0 0 16 16" width="18" height="18" fill="currentColor"><path d="M8 1a7 7 0 100 14A7 7 0 008 1zm0 1.2a5.8 5.8 0 110 11.6A5.8 5.8 0 018 2.2zM7.4 5v1.4H6v1.2h1.4V9H6v1.2h1.4v1.4h1.2v-1.4H10V9H8.6V7.6H10V6.4H8.6V5H7.4z"/></svg>
          <div><div class="resource-card-name">KVR Audio</div><div class="resource-card-domain">kvraudio.com</div></div>
        </a>`);
        const pbQuery = encodeURIComponent(p.name);
        resourceCards.push(`<a href="https://www.pluginboutique.com/search?q=${pbQuery}" class="resource-card" target="_blank" rel="noopener">
          <svg class="resource-card-icon" viewBox="0 0 16 16" width="18" height="18" fill="currentColor"><path d="M2 2a2 2 0 00-2 2v1h16V4a2 2 0 00-2-2H2zm0 5v5a2 2 0 002 2h8a2 2 0 002-2V7H2zm3 2h6v1H5V9z"/></svg>
          <div><div class="resource-card-name">Plugin Boutique</div><div class="resource-card-domain">pluginboutique.com</div></div>
        </a>`);
      }
      const resourcesSection = resourceCards.length ? `<section class="pd-section">
        <h2 class="pd-section-title">Resources</h2>
        <div class="pd-resources-grid">${resourceCards.join('')}</div>
      </section>` : '';

      // Placeholders — only filled if results come back
      const similarSection = '<div id="similar-section"></div>';
      const freeAltPlaceholder = p.price_type !== 'free' ? '<div id="free-alternatives-section"></div>' : '';

      const moreSection = hasMfrPlugins ? `<section class="pd-section">
        <h2 class="pd-section-title">More from ${escapeHtml(mfr.name)} <a href="#/manufacturers/${escapeHtml(mfr.slug)}" class="section-link">View all &rarr;</a></h2>
        ${pluginGrid(p.manufacturer_plugins)}
      </section>` : '';

      let html = `
        <nav class="breadcrumb"><a href="#/">Plugins</a> <span class="bc-sep">/</span> <span class="bc-current">${escapeHtml(p.name)}</span></nav>
        ${heroHtml}
        ${titleHtml}
        ${detailsSection}
        ${tagsSection}
        ${resourcesSection}
        ${similarSection}
        ${freeAltPlaceholder}
        ${moreSection}`;

      app.innerHTML = html;
      wireImageLoading(app);

      // Similar plugins (async, carousel)
      if (p.id) {
        try {
          const sim = await API.get(`/plugins/${p.id}/similar`, { limit: 8 });
          const section = document.getElementById('similar-section');
          if (sim.data && sim.data.length && section) {
            section.innerHTML = `<section class="pd-section"><h2 class="pd-section-title">Similar Plugins <span class="section-count">${sim.total} found</span></h2>${pluginCarousel(sim.data)}</section>`;
            wireImageLoading(section);
          }
          // If no results, section stays empty — no "no results" message cluttering the page
        } catch (_) {
          // Silently skip — similar plugins are non-critical
        }
      }

      // Free alternatives (only for paid plugins)
      if (p.price_type !== 'free') {
        try {
          const params = { category: p.category, price_type: 'free', per_page: 6 };
          if (p.subcategory) params.subcategory = p.subcategory;
          const freeAlt = await API.get('/plugins', params);
          const faSection = document.getElementById('free-alternatives-section');
          if (freeAlt.data && freeAlt.data.length && faSection) {
            faSection.innerHTML = `<section class="pd-section"><h2 class="pd-section-title">Free Alternatives <span class="section-count">${freeAlt.total} found</span></h2>${pluginGrid(freeAlt.data)}</section>`;
            wireImageLoading(faSection);
          }
        } catch (_) { /* silently skip if free alternatives fail */ }
      }
    } catch (err) { showError(app, err.message); }
  };

  // == MANUFACTURER LIST ==
  Views.manufacturers = async function (params) {
    document.title = 'Manufacturers - PluginDB';
    const app = document.getElementById('app');
    const search = params.get('search') || '';
    const sort = params.get('sort') || 'name';
    const order = params.get('order') || 'asc';
    const page = parseInt(params.get('page'), 10) || 1;

    const mfrSortVal = sort + '_' + order;
    app.innerHTML = `
      <section class="page-header"><h1>Manufacturers</h1></section>
      <section class="browse-section">
        <div class="filter-bar">
          <div class="search-input-wrap" style="flex:1">
            <svg class="search-icon" viewBox="0 0 16 16" fill="currentColor"><path d="M11.742 10.344a6.5 6.5 0 10-1.397 1.398h-.001l3.85 3.85a1 1 0 001.415-1.414l-3.85-3.85-.017.016zm-5.242.156a5 5 0 110-10 5 5 0 010 10z"/></svg>
            <input id="mfr-search" type="search" class="search-input" placeholder="Search manufacturers\u2026" value="${escapeHtml(search)}" autocomplete="off" aria-label="Search manufacturers">
            <button id="mfr-search-clear" class="search-clear${search ? ' visible' : ''}" aria-label="Clear search" type="button">&times;</button>
            <span class="search-shortcut">/</span>
          </div>
          <select id="mfr-sort" class="mfr-sort-select" aria-label="Sort manufacturers">
            <option value="name_asc"${mfrSortVal === 'name_asc' ? ' selected' : ''}>Name A-Z</option>
            <option value="name_desc"${mfrSortVal === 'name_desc' ? ' selected' : ''}>Name Z-A</option>
            <option value="plugin_count_desc"${mfrSortVal === 'plugin_count_desc' ? ' selected' : ''}>Most plugins</option>
          </select>
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

    var mfrSearchInput = document.getElementById('mfr-search');
    mfrSearchInput.addEventListener('input', debounce(function () {
      var clearBtn = document.getElementById('mfr-search-clear');
      if (clearBtn) clearBtn.classList.toggle('visible', mfrSearchInput.value.length > 0);
      location.hash = buildHash({ search: this.value.trim(), page: undefined });
    }, CONFIG.DEBOUNCE_MS));

    var mfrSearchClear = document.getElementById('mfr-search-clear');
    if (mfrSearchClear) {
      mfrSearchClear.addEventListener('click', function() {
        mfrSearchInput.value = '';
        this.classList.remove('visible');
        location.hash = buildHash({ search: '', page: undefined });
        mfrSearchInput.focus();
      });
    }

    document.getElementById('mfr-sort').addEventListener('change', function () {
      var parts = this.value.split('_');
      var nextSort = parts[0] + (parts.length > 2 ? '_' + parts[1] : '');
      var nextOrd = parts[parts.length - 1];
      location.hash = buildHash({ sort: nextSort, order: nextOrd });
    });

    const resultsArea = document.getElementById('results-area');
    const paginationArea = document.getElementById('pagination-area');
    try {
      const data = await API.get('/manufacturers', { search: search || undefined, sort, order, page, per_page: CONFIG.ITEMS_PER_PAGE });
      if (!data.data || !data.data.length) { showEmpty(resultsArea, 'No manufacturers found.'); return; }
      // Cycle 14: Richer manufacturer cards
      resultsArea.innerHTML = '<div class="mfr-grid">' + data.data.map(m => {
        const initials = (m.name || '').split(/[\s-]+/).slice(0, 2).map(w => w.charAt(0)).join('').toUpperCase();
        return `<a href="#/manufacturers/${escapeHtml(m.slug)}" class="mfr-card">
          <div class="mfr-card-top">
            <div class="mfr-card-icon">${escapeHtml(initials)}</div>
            <div>
              <h3>${escapeHtml(m.name)}</h3>
              <span class="mfr-card-count">${m.plugin_count} plugin${m.plugin_count !== 1 ? 's' : ''}</span>
            </div>
          </div>
          ${m.website ? `<div class="mfr-card-bottom"><span class="mfr-website">${escapeHtml(m.website.replace(/^https?:\/\//, ''))}</span></div>` : ''}
        </a>`;
      }).join('') + '</div>';
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
      document.title = `${m.name} - PluginDB`;

      // Compute stats
      const catCount = Object.keys(data.categories || {}).length;
      const catBreakdown = Object.entries(data.categories || {}).map(([c, n]) => `${escapeHtml(c)} (${n})`).join(', ');

      // Compute year range from all plugins
      const allYears = (data.plugins || []).map(function(p) { return p.year; }).filter(function(y) { return y != null; });
      const yearMin = allYears.length ? Math.min.apply(null, allYears) : null;
      const yearMax = allYears.length ? Math.max.apply(null, allYears) : null;
      const yearRangeStr = yearMin && yearMax ? (yearMin === yearMax ? String(yearMin) : yearMin + ' \u2013 ' + yearMax) : '\u2014';

      // Website link
      const websiteHtml = m.website ? `<a href="${escapeHtml(m.website)}" class="mfr-website-link" target="_blank" rel="noopener">
        <svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor"><path d="M8 0a8 8 0 100 16A8 8 0 008 0zm-.5 1.07A6.97 6.97 0 001.05 7H4.1a18 18 0 01.4-4.43c.62-.22 1.28-.38 1.97-.46L7.5 1.07zM8.5 1.07l1.03 1.04c.69.08 1.35.24 1.97.46.26 1.35.38 2.86.4 4.43h3.05A6.97 6.97 0 008.5 1.07zM5.15 7a17 17 0 00-.05.5V8h5.8v-.5a17 17 0 00-.05-.5H5.15zm-1.05 0H1.05a6.97 6.97 0 006.45 7.93l-1.03-1.04c-.69-.08-1.35-.24-1.97-.46A17 17 0 014.1 9zm7.8 0a17 17 0 01-.4 4.43c-.62.22-1.28.38-1.97.46l-1.03 1.04A6.97 6.97 0 0014.95 9H11.9z"/></svg>
        ${escapeHtml(m.website.replace(/^https?:\/\//, ''))}
      </a>` : '';

      // Category breakdown as links to browse page (filtered by this manufacturer)
      const categories = Object.entries(data.categories || {});
      let catLinksHtml = '';
      if (categories.length > 1) {
        catLinksHtml = '<div class="mfr-cat-pills">' +
          categories.map(function([c, n]) {
            return `<a href="#/?manufacturer=${escapeHtml(slug)}&category=${escapeHtml(c)}" class="cat-pill">${escapeHtml(c)} <span class="cat-pill-count">${n}</span></a>`;
          }).join('') + '</div>';
      }

      let html = `
        <nav class="breadcrumb"><a href="#/manufacturers">Manufacturers</a> <span class="bc-sep">/</span> <span class="bc-current">${escapeHtml(m.name)}</span></nav>
        <div class="pd-title-bar">
          <h1 class="pd-name">${escapeHtml(m.name)}</h1>
          <div class="pd-title-meta">
            ${websiteHtml}
          </div>
        </div>
        <div class="mfr-detail-stats">
          <div class="mfr-stat-card"><div class="mfr-stat-num">${data.plugin_count}</div><div class="mfr-stat-label">Plugins</div></div>
          <div class="mfr-stat-card"><div class="mfr-stat-num">${catCount}</div><div class="mfr-stat-label">Categor${catCount !== 1 ? 'ies' : 'y'}</div></div>
          <div class="mfr-stat-card"><div class="mfr-stat-num">${escapeHtml(yearRangeStr)}</div><div class="mfr-stat-label">Year Range</div></div>
        </div>`;

      if (data.plugins && data.plugins.length) {
        const bh = '#/manufacturers/' + encodeURIComponent(slug);
        html += `<section class="pd-section">
          <h2 class="pd-section-title">Plugins</h2>
          ${catLinksHtml}
          ${pluginGrid(data.plugins)}
          ${renderPagination(data.pagination, bh)}
        </section>`;
      } else {
        html += '<section class="pd-section"><p style="color:var(--text-muted)">No plugins listed yet.</p></section>';
      }
      app.innerHTML = html;
      wireImageLoading(app);

      // Category pills are now links — no click handler needed
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

    const pluginMatch = path.match(/^\/plugins\/(.+)$/);
    if (pluginMatch) { updateNav('home'); return Views.pluginDetail(decodeURIComponent(pluginMatch[1])); }

    const mfrMatch = path.match(/^\/manufacturers\/(.+)$/);
    if (mfrMatch) { updateNav('manufacturers'); return Views.manufacturerDetail(decodeURIComponent(mfrMatch[1]), params); }

    if (path === '/manufacturers') { updateNav('manufacturers'); return Views.manufacturers(params); }

    updateNav('home');
    return Views.home(params);
  }

  // ---- CYCLE 1: Header scroll shadow ----
  let lastScrollY = 0;
  window.addEventListener('scroll', function() {
    const header = document.getElementById('site-header');
    if (window.scrollY > 10) header.classList.add('scrolled');
    else header.classList.remove('scrolled');
    lastScrollY = window.scrollY;

    // Cycle 18: Scroll to top visibility
    const scrollBtn = document.getElementById('scroll-top');
    if (scrollBtn) {
      if (window.scrollY > 400) scrollBtn.classList.add('visible');
      else scrollBtn.classList.remove('visible');
    }
  }, { passive: true });

  // Global keyboard shortcut: / focuses search
  document.addEventListener('keydown', function (e) {
    if (e.key === '/' && !e.ctrlKey && !e.metaKey && document.activeElement.tagName !== 'INPUT') {
      e.preventDefault();
      const si = document.getElementById('search-input') || document.getElementById('mfr-search');
      if (si) si.focus();
    }
  });

  // Close suggest dropdown when clicking outside
  document.addEventListener('click', function (e) {
    if (!e.target.closest('.search-wrap') && !e.target.closest('.search-input-wrap')) {
      var dd = document.getElementById('suggest-dropdown');
      if (dd) dd.classList.add('hidden');
    }
  });

  // Cycle 18: Create scroll-to-top button
  var scrollTopBtn = document.createElement('button');
  scrollTopBtn.id = 'scroll-top';
  scrollTopBtn.className = 'scroll-top';
  scrollTopBtn.setAttribute('aria-label', 'Scroll to top');
  scrollTopBtn.innerHTML = '<svg viewBox="0 0 16 16" fill="currentColor"><path d="M8 3l5 5h-3v4H6V8H3l5-5z"/></svg>';
  scrollTopBtn.addEventListener('click', function() { window.scrollTo({ top: 0, behavior: 'smooth' }); });
  document.body.appendChild(scrollTopBtn);

  window.addEventListener('hashchange', router);
  router();
})();
