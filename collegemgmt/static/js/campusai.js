/**
 * CampusAI  —  campusai.js
 * Shared UI behaviour: theme, sidebar, toasts, counters, skeleton,
 * ripple, confirm modals, sortable tables, password strength.
 * No dependencies beyond Bootstrap 5 bundle (already on page).
 */

/* ── Utility ────────────────────────────────────────────────────── */
const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];
const reducedMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ── 1. Theme Picker ─────────────────────────────────────────────── */
(function initTheme() {
  'use strict';

  // ── Constants ──────────────────────────────────────────────────
  var VALID_THEMES  = ['light','dark','ocean','forest','sunset','midnight','hi-contrast','system'];
  var DARK_BS       = new Set(['dark','ocean','forest','sunset','midnight']);
  var STORAGE_KEY   = 'campusai-theme';
  var DEFAULT_THEME = 'light';

  // Themes that map to a real data-theme attribute (system resolves at runtime)
  var THEME_META = [
    { id:'light',       label:'Light',      icon:'bi-sun-fill' },
    { id:'dark',        label:'Dark',       icon:'bi-moon-stars-fill' },
    { id:'ocean',       label:'Ocean',      icon:'bi-water' },
    { id:'forest',      label:'Forest',     icon:'bi-tree-fill' },
    { id:'sunset',      label:'Sunset',     icon:'bi-sunset-fill' },
    { id:'midnight',    label:'Midnight',   icon:'bi-moon-fill' },
    { id:'hi-contrast', label:'Contrast',   icon:'bi-circle-half' },
    { id:'system',      label:'System',     icon:'bi-display' },
  ];

  // ── Safe localStorage ──────────────────────────────────────────
  function storageGet(key, fallback) {
    try { return localStorage.getItem(key) || fallback; } catch(e) { return fallback; }
  }
  function storageSet(key, val) {
    try { localStorage.setItem(key, val); } catch(e) {}
  }

  // ── Resolve system preference ──────────────────────────────────
  function systemPrefersDark() {
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  }

  // ── Apply a resolved (non-system) theme to the DOM ───────────
  function applyResolved(resolved) {
    var html = document.documentElement;
    html.setAttribute('data-theme', resolved);
    html.setAttribute('data-bs-theme', DARK_BS.has(resolved) ? 'dark' : 'light');
  }

  // ── Resolve 'system' → actual theme name ─────────────────────
  function resolve(theme) {
    if (theme === 'system') return systemPrefersDark() ? 'dark' : 'light';
    return theme;
  }

  // ── Apply any theme (including 'system') ──────────────────────
  var _sysMQL      = null;   // active matchMedia listener
  var _sysMQLFn    = null;   // the handler function reference

  function applyTheme(theme) {
    // Whitelist check — never write raw stored value
    if (!VALID_THEMES.includes(theme)) theme = DEFAULT_THEME;

    // Clean up old system listener if we're switching away
    if (_sysMQL && _sysMQLFn) {
      try { _sysMQL.removeEventListener('change', _sysMQLFn); } catch(e) {
        try { _sysMQL.removeListener(_sysMQLFn); } catch(e2) {}
      }
      _sysMQL = null; _sysMQLFn = null;
    }

    if (theme === 'system') {
      applyResolved(resolve('system'));
      // Re-apply whenever OS pref changes
      if (window.matchMedia) {
        _sysMQL   = window.matchMedia('(prefers-color-scheme: dark)');
        _sysMQLFn = function() { applyResolved(resolve('system')); };
        try { _sysMQL.addEventListener('change', _sysMQLFn); } catch(e) {
          try { _sysMQL.addListener(_sysMQLFn); } catch(e2) {}
        }
      }
    } else {
      applyResolved(theme);
    }
    storageSet(STORAGE_KEY, theme);
    updatePickerUI(theme);
  }

  // ── Update all picker button aria states ──────────────────────
  function updatePickerUI(theme) {
    document.querySelectorAll('.theme-option').forEach(function(btn) {
      btn.setAttribute('aria-pressed', btn.dataset.theme === theme ? 'true' : 'false');
    });
    // Update trigger button icon
    var icon = THEME_META.find(function(t) { return t.id === theme; });
    document.querySelectorAll('.theme-picker-btn i').forEach(function(el) {
      el.className = 'bi ' + (icon ? icon.icon : 'bi-palette');
    });
    document.querySelectorAll('.theme-picker-btn').forEach(function(btn) {
      btn.setAttribute('aria-label', 'Theme: ' + (icon ? icon.label : theme));
    });
  }

  // ── Bootstrap: build picker HTML ────────────────────────────
  function buildPicker() {
    var grid = THEME_META.filter(function(t) { return t.id !== 'system'; });
    var html = '<div class="theme-picker-label">Choose theme</div>'
      + '<div class="theme-picker-grid" role="group" aria-label="Theme options">';
    grid.forEach(function(t) {
      html += '<button class="theme-option" data-theme="' + t.id + '"'
        + ' role="button" aria-pressed="false"'
        + ' aria-label="' + t.label + ' theme">'
        + '<span class="theme-swatch" data-swatch="' + t.id + '"></span>'
        + '<span class="theme-option-name">' + t.label + '</span>'
        + '</button>';
    });
    html += '</div>';
    // System row
    var sys = THEME_META.find(function(t) { return t.id === 'system'; });
    html += '<div class="theme-picker-divider"></div>'
      + '<button class="theme-option theme-option-system" data-theme="system"'
      + ' role="button" aria-pressed="false" aria-label="System/Auto theme">'
      + '<span class="theme-swatch" data-swatch="system"></span>'
      + '<span class="theme-option-name">System / Auto</span>'
      + '</button>';
    return html;
  }

  // ── Wire up all picker instances ──────────────────────────────
  function initPickers() {
    var pickers = document.querySelectorAll('.theme-picker-wrap');
    if (!pickers.length) return;

    pickers.forEach(function(wrap) {
      var btn     = wrap.querySelector('.theme-picker-btn');
      var popover = wrap.querySelector('.theme-picker-popover');
      if (!btn || !popover) return;

      // Inject content once
      popover.innerHTML = buildPicker();

      // Toggle open/close
      function togglePopover(open) {
        if (open === undefined) open = !popover.classList.contains('open');
        popover.classList.toggle('open', open);
        btn.setAttribute('aria-expanded', open ? 'true' : 'false');
        if (open) {
          // Focus first option
          var first = popover.querySelector('.theme-option');
          if (first) first.focus();
        }
      }

      btn.addEventListener('click', function(e) {
        e.stopPropagation();
        togglePopover();
      });

      // Click on a theme option
      popover.addEventListener('click', function(e) {
        var opt = e.target.closest('.theme-option');
        if (!opt) return;
        var chosen = opt.dataset.theme;
        applyTheme(chosen);
        togglePopover(false);
        btn.focus();
      });

      // Keyboard navigation within popover
      popover.addEventListener('keydown', function(e) {
        var opts = Array.from(popover.querySelectorAll('.theme-option'));
        var idx  = opts.indexOf(document.activeElement);
        if (e.key === 'Escape') {
          togglePopover(false); btn.focus(); return;
        }
        if (e.key === 'Enter' || e.key === ' ') {
          var opt = e.target.closest('.theme-option');
          if (opt) { e.preventDefault(); applyTheme(opt.dataset.theme); togglePopover(false); btn.focus(); }
          return;
        }
        if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
          e.preventDefault();
          var next = opts[(idx + 1) % opts.length]; if (next) next.focus();
        }
        if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
          e.preventDefault();
          var prev = opts[(idx - 1 + opts.length) % opts.length]; if (prev) prev.focus();
        }
      });
    });

    // Close on outside click
    document.addEventListener('click', function() {
      document.querySelectorAll('.theme-picker-popover.open').forEach(function(p) {
        p.classList.remove('open');
        var b = p.closest('.theme-picker-wrap') && p.closest('.theme-picker-wrap').querySelector('.theme-picker-btn');
        if (b) b.setAttribute('aria-expanded', 'false');
      });
    });
  }

  // ── Initial load ────────────────────────────────────────────
  var saved = storageGet(STORAGE_KEY, DEFAULT_THEME);
  // Validate against whitelist
  if (!VALID_THEMES.includes(saved)) saved = DEFAULT_THEME;
  // Apply immediately (head inline script already did the visual part; this syncs data-bs-theme)
  applyTheme(saved);

  document.addEventListener('DOMContentLoaded', function() {
    initPickers();
    updatePickerUI(saved);
  });
})();

/* ── 2. Sidebar ─────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  const sidebar  = $('#appSidebar');
  const overlay  = $('#sidebarOverlay');
  const toggle   = $('#sidebarToggle');
  if (!sidebar) return;

  const open  = () => { sidebar.classList.add('open'); overlay && overlay.classList.add('show'); };
  const close = () => { sidebar.classList.remove('open'); overlay && overlay.classList.remove('show'); };

  toggle  && toggle.addEventListener('click',  open);
  overlay && overlay.addEventListener('click', close);

  /* close on ESC */
  document.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });

  /* Active link highlighting */
  const path = window.location.pathname;
  $$('.sidebar-link', sidebar).forEach(link => {
    const href = link.getAttribute('href');
    if (href && href !== '/' && path.startsWith(href)) {
      link.classList.add('active');
    }
  });
});

/* ── 3. Toast Notifications ─────────────────────────────────────── */
window.CampusToast = (function () {
  function ensureContainer() {
    let c = $('#toast-container');
    if (!c) {
      c = document.createElement('div');
      c.id = 'toast-container';
      document.body.appendChild(c);
    }
    return c;
  }

  const icons = {
    success: 'bi-check-circle-fill',
    error:   'bi-x-circle-fill',
    warning: 'bi-exclamation-triangle-fill',
    info:    'bi-info-circle-fill',
  };
  const labels = { success:'Success', error:'Error', warning:'Warning', info:'Info' };

  function show(msg, type = 'info', dur = 4500) {
    const c    = ensureContainer();
    const el   = document.createElement('div');
    el.className = `toast-msg ${type}`;
    el.innerHTML = `
      <i class="bi ${icons[type] || icons.info} toast-icon"></i>
      <div class="toast-body">
        <div class="toast-title">${labels[type] || 'Notice'}</div>
        <div>${msg}</div>
      </div>
      <button class="toast-close" aria-label="Close"><i class="bi bi-x-lg"></i></button>`;
    c.appendChild(el);

    const dismiss = () => {
      el.classList.add('toast-hide');
      setTimeout(() => el.remove(), 350);
    };
    el.querySelector('.toast-close').addEventListener('click', dismiss);
    setTimeout(dismiss, dur);
  }

  return { show, success: m => show(m,'success'), error: m => show(m,'error'),
           warning: m => show(m,'warning'), info: m => show(m,'info') };
})();

/* ── 4. Convert Django messages → Toasts ───────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  $$('.django-message[data-msg]').forEach(el => {
    const msg  = el.dataset.msg;
    const tags = (el.dataset.tags || '').toLowerCase();
    const type = tags.includes('success') ? 'success'
               : tags.includes('error')   ? 'error'
               : tags.includes('warning') ? 'warning'
               : 'info';
    CampusToast.show(msg, type);
    el.remove();
  });
});

/* ── 5. Animated Number Counters ────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  if (reducedMotion()) return;

  const animate = (el) => {
    const target  = parseFloat(el.dataset.target || el.textContent.replace(/[^0-9.]/g, '')) || 0;
    const suffix  = el.dataset.suffix || '';
    const dur     = parseInt(el.dataset.dur, 10) || 1200;
    const start   = performance.now();
    el.textContent = '0' + suffix;

    const step = (now) => {
      const t    = Math.min((now - start) / dur, 1);
      const ease = 1 - Math.pow(1 - t, 3);           /* easeOutCubic */
      const val  = target % 1 === 0
                   ? Math.round(ease * target)
                   : (ease * target).toFixed(1);
      el.textContent = val + suffix;
      if (t < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  };

  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) { animate(e.target); obs.unobserve(e.target); }
    });
  }, { threshold: 0.3 });

  $$('.count-up').forEach(el => obs.observe(el));
});

/* ── 6. Progress Ring Animation ─────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  $$('.progress-ring-fill').forEach(circle => {
    const pct    = parseFloat(circle.dataset.pct || 0);
    const r      = parseFloat(circle.getAttribute('r') || 36);
    const circ   = 2 * Math.PI * r;
    circle.style.strokeDasharray  = circ;
    circle.style.strokeDashoffset = circ;  /* start empty */

    const run = () => {
      const offset = circ - (pct / 100) * circ;
      if (reducedMotion()) {
        circle.style.strokeDashoffset = offset;
      } else {
        setTimeout(() => { circle.style.strokeDashoffset = offset; }, 200);
      }
    };

    const obs = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting) { run(); obs.disconnect(); }
    }, { threshold: 0.3 });
    obs.observe(circle);
  });
});

/* ── 7. Animated Progress Bars ───────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  $$('.progress-bar[data-pct]').forEach(bar => {
    const pct = bar.dataset.pct || 0;
    bar.style.width = '0%';
    const run = () => {
      if (reducedMotion()) { bar.style.width = pct + '%'; return; }
      setTimeout(() => {
        bar.style.transition = 'width 1s cubic-bezier(0.16,1,0.3,1)';
        bar.style.width = pct + '%';
      }, 150);
    };
    const obs = new IntersectionObserver(e => { if (e[0].isIntersecting) { run(); obs.disconnect(); } });
    obs.observe(bar);
  });
});

/* ── 8. Card Tilt (3-D hover) ────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  if (reducedMotion()) return;
  $$('.card-tilt').forEach(card => {
    card.addEventListener('mousemove', e => {
      const r   = card.getBoundingClientRect();
      const x   = ((e.clientX - r.left) / r.width  - 0.5) * 10;
      const y   = ((e.clientY - r.top)  / r.height - 0.5) * -10;
      card.style.transform = `perspective(800px) rotateX(${y}deg) rotateY(${x}deg) translateY(-4px)`;
    });
    card.addEventListener('mouseleave', () => {
      card.style.transform = '';
    });
  });
});

/* ── 9. Submit-button loading state ──────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  $$('form').forEach(form => {
    const btn = form.querySelector('[type="submit"]');
    if (!btn) return;
    form.addEventListener('submit', () => {
      /* small delay so form validation can fire first */
      requestAnimationFrame(() => {
        if (form.checkValidity && !form.checkValidity()) return;
        btn.classList.add('btn-loading');
        btn.setAttribute('disabled', '');
      });
    });
  });
});

/* ── 10. Password visibility toggle ──────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  $$('.password-toggle-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const id    = btn.dataset.target;
      const input = document.getElementById(id);
      if (!input) return;
      const isPass = input.type === 'password';
      input.type   = isPass ? 'text' : 'password';
      const icon   = btn.querySelector('i');
      if (icon) icon.className = isPass ? 'bi bi-eye-slash-fill' : 'bi bi-eye-fill';
      btn.setAttribute('aria-label', isPass ? 'Hide password' : 'Show password');
    });
  });
});

/* ── 11. Password Strength Meter ─────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  const pwInput  = document.getElementById('id_password') || document.getElementById('id_password1');
  const strengthWrap = document.getElementById('pw-strength-wrap');
  if (!pwInput || !strengthWrap) return;

  pwInput.addEventListener('input', () => {
    const v = pwInput.value;
    let score = 0;
    if (v.length >= 8)        score++;
    if (/[A-Z]/.test(v))      score++;
    if (/[0-9]/.test(v))      score++;
    if (/[^A-Za-z0-9]/.test(v)) score++;

    const fill  = strengthWrap.querySelector('.pw-strength-fill');
    const label = strengthWrap.querySelector('.pw-strength-label');
    const colors = ['#ef4444','#f59e0b','#10b981','#5b4cf5'];
    const labels = ['Weak','Fair','Good','Strong'];

    if (!fill || !label) return;
    fill.style.width  = (score * 25) + '%';
    fill.style.background = colors[score - 1] || '#ef4444';
    label.textContent  = v.length ? labels[score - 1] || 'Weak' : '';
    label.style.color  = colors[score - 1] || '';
  });
});

/* ── 12. Confirm Modal helper ────────────────────────────────────── */
window.CampusConfirm = function (opts) {
  /* opts: { title, body, confirmText, confirmClass, onConfirm } */
  const id  = 'campus-confirm-modal';
  let modal = document.getElementById(id);
  if (!modal) {
    modal = document.createElement('div');
    modal.id = id;
    modal.className = 'modal fade';
    modal.setAttribute('tabindex', '-1');
    modal.innerHTML = `
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content confirm-modal">
          <div class="modal-header border-0 pb-0">
            <h5 class="modal-title fw-bold" id="cc-title"></h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body" id="cc-body"></div>
          <div class="modal-footer border-0 pt-0">
            <button class="btn btn-outline-secondary rounded-3" data-bs-dismiss="modal">Cancel</button>
            <button class="btn rounded-3" id="cc-ok"></button>
          </div>
        </div>
      </div>`;
    document.body.appendChild(modal);
  }
  modal.querySelector('#cc-title').textContent = opts.title || 'Confirm';
  modal.querySelector('#cc-body').innerHTML    = opts.body  || '';
  const ok = modal.querySelector('#cc-ok');
  ok.textContent = opts.confirmText  || 'Confirm';
  ok.className   = `btn rounded-3 ${opts.confirmClass || 'btn-danger'}`;

  const bsModal = new bootstrap.Modal(modal);
  bsModal.show();

  /* Replace listener */
  const newOk = ok.cloneNode(true);
  ok.parentNode.replaceChild(newOk, ok);
  newOk.addEventListener('click', () => {
    bsModal.hide();
    opts.onConfirm && opts.onConfirm();
  });
};

/* ── 13. Inline table search ─────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  $$('[data-table-search]').forEach(input => {
    const tableId = input.dataset.tableSearch;
    const table   = document.getElementById(tableId);
    if (!table) return;
    input.addEventListener('input', () => {
      const q = input.value.toLowerCase();
      $$('tbody tr', table).forEach(row => {
        row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
      });
    });
  });
});

/* ── 14. Sortable table columns ──────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  $$('table.sortable-table').forEach(table => {
    const headers = $$('thead th.sortable', table);
    let lastCol = null, lastDir = 'asc';

    headers.forEach((th, idx) => {
      th.addEventListener('click', () => {
        const dir = (th === lastCol && lastDir === 'asc') ? 'desc' : 'asc';
        lastCol = th; lastDir = dir;
        headers.forEach(h => h.classList.remove('sort-asc','sort-desc'));
        th.classList.add(dir === 'asc' ? 'sort-asc' : 'sort-desc');

        const rows = $$('tbody tr', table);
        rows.sort((a, b) => {
          const av = (a.cells[idx]?.textContent || '').trim();
          const bv = (b.cells[idx]?.textContent || '').trim();
          const n  = parseFloat(av) - parseFloat(bv);
          const cmp = isNaN(n) ? av.localeCompare(bv) : n;
          return dir === 'asc' ? cmp : -cmp;
        });
        const tbody = table.querySelector('tbody');
        rows.forEach(r => tbody.appendChild(r));
      });
    });
  });
});

/* ── 15. Notification dropdown toggle ────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  const bell     = $('#notifBell');
  const dropdown = $('#notifDropdown');
  if (!bell || !dropdown) return;

  bell.addEventListener('click', e => {
    e.stopPropagation();
    const showing = dropdown.style.display === 'block';
    dropdown.style.display = showing ? 'none' : 'block';
  });
  document.addEventListener('click', () => {
    if (dropdown) dropdown.style.display = 'none';
  });
});

/* ── 16. AOS-like scroll reveal (IntersectionObserver) ──────────── */
document.addEventListener('DOMContentLoaded', () => {
  if (reducedMotion()) return;
  if (typeof AOS !== 'undefined') { AOS.init({ duration:600, once:true, easing:'ease-out-cubic' }); return; }

  /* Fallback: manual fade+slide */
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.style.opacity   = '1';
        e.target.style.transform = 'translateY(0)';
        obs.unobserve(e.target);
      }
    });
  }, { threshold: 0.1 });

  $$('[data-reveal]').forEach((el, i) => {
    el.style.opacity   = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = `opacity 0.5s ease ${i * 0.06}s, transform 0.5s ease ${i * 0.06}s`;
    obs.observe(el);
  });
});

/* ── 17. Staggered list animation ────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  if (reducedMotion()) return;
  $$('[data-stagger]').forEach(parent => {
    $$(':scope > *', parent).forEach((child, i) => {
      child.style.opacity   = '0';
      child.style.transform = 'translateY(14px)';
      child.style.transition = `opacity 0.4s ease ${i * 0.07}s, transform 0.4s ease ${i * 0.07}s`;
    });
    const obs = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting) {
        $$(':scope > *', parent).forEach(child => {
          child.style.opacity   = '1';
          child.style.transform = 'translateY(0)';
        });
        obs.disconnect();
      }
    }, { threshold: 0.05 });
    obs.observe(parent);
  });
});

/* ── 18. Page fade-in ────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  if (reducedMotion()) return;
  const content = $('.page-content') || document.querySelector('main') || document.querySelector('.dash-wrapper');
  if (content) content.classList.add('page-fade-in');
});

/* ── 19. Nav link active (topbar for auth pages) ─────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  const path = window.location.pathname;
  $$('.nav-link-custom').forEach(link => {
    const href = link.getAttribute('href');
    if (href && href !== '/' && path.startsWith(href)) {
      link.classList.add('active');
    }
  });
});
