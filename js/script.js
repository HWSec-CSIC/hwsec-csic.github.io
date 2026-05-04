// Minimal interactions: mobile nav and reveal-on-scroll

(function() {
  const body = document.body;
  const themeToggle = document.querySelector('.theme-toggle');
  const themeIcon = themeToggle ? themeToggle.querySelector('.theme-toggle-icon') : null;
  const themeColorMetas = Array.from(document.querySelectorAll('meta[name="theme-color"]'));
  const themeStorageKey = 'theme-preference';
  const themeQuery = window.matchMedia('(prefers-color-scheme: dark)');
  const lightThemeColor = '#ffffff';
  const darkThemeColor = '#0b0d12';

  const getPreferredTheme = () => {
    try {
      const stored = localStorage.getItem(themeStorageKey);
      if (stored === 'dark' || stored === 'light') {
        return stored;
      }
    } catch (e) {}
    return themeQuery.matches ? 'dark' : 'light';
  };

  const applyTheme = (theme, persist) => {
    const isDark = theme === 'dark';
    const themeColor = isDark ? darkThemeColor : lightThemeColor;
    document.documentElement.classList.toggle('dark', isDark);
    body.classList.toggle('dark-theme', isDark);
    body.classList.toggle('theme-light', !isDark);
    body.style.colorScheme = isDark ? 'dark' : 'light';
    themeColorMetas.forEach((meta) => {
      meta.setAttribute('content', themeColor);
    });
    if (themeToggle) {
      themeToggle.setAttribute('aria-pressed', String(isDark));
      themeToggle.setAttribute('aria-label', isDark ? 'Switch to light theme' : 'Switch to dark theme');
    }
    if (themeIcon) {
      themeIcon.textContent = isDark ? '☀' : '☾';
    }
    if (persist) {
      try {
        localStorage.setItem(themeStorageKey, theme);
      } catch (e) {}
    }
  };

  applyTheme(getPreferredTheme(), false);
  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      applyTheme(body.classList.contains('dark-theme') ? 'light' : 'dark', true);
    });
  }

  // Mobile menu toggle (Tailwind design has simpler nav, no complex menu toggle needed)
  // This code is kept for compatibility with custom navigation if needed
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.site-nav');
  const links = nav ? document.querySelectorAll('.site-nav a') : [];
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const isOpen = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(isOpen));
    });
    // Close menu on link click (mobile)
    links.forEach((a) => a.addEventListener('click', () => {
      if (nav.classList.contains('open')) {
        nav.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    }));
  }

  // Smooth scroll
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!prefersReduced) {
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
      anchor.addEventListener('click', function (e) {
        const id = this.getAttribute('href');
        if (id.length > 1) {
          const target = document.querySelector(id);
          if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
        }
      });
    });
  }

  // Reveal on scroll
  const els = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && els.length) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('revealed');
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.1 });
    els.forEach((el) => io.observe(el));
  } else {
    els.forEach((el) => el.classList.add('revealed'));
  }

  // Scroll spy - updated to work with new Tailwind nav structure
  const sections = document.querySelectorAll('section[id]');
  // Try to find nav links in new structure first, fallback to old structure
  let navLinks = Array.from(document.querySelectorAll('nav a[href^="#"]'));
  if (navLinks.length === 0) {
    navLinks = Array.from(document.querySelectorAll('.site-nav a[href^="#"]'));
  }
  if ('IntersectionObserver' in window && sections.length && navLinks.length) {
    const activeClass = 'active';
    const byId = new Map(navLinks.map((a) => [a.getAttribute('href').replace('#', ''), a]));
    const spy = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        const id = entry.target.id;
        const link = byId.get(id);
        if (!link) return;
        if (entry.isIntersecting) {
          navLinks.forEach((a) => a.classList.remove(activeClass));
          link.classList.add(activeClass);
        }
      });
    }, { rootMargin: '-30% 0px -60% 0px', threshold: 0.1 });
    sections.forEach((s) => spy.observe(s));
  }

  // Back to top button - only if element exists
  const toTop = document.querySelector('.to-top');
  if (toTop) {
    const onScroll = () => {
      toTop.hidden = window.scrollY <= 320;
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    toTop.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: prefersReduced ? 'auto' : 'smooth' });
    });
    onScroll();
  }

  // Auto-hide header - only if header element exists
  (function headerAutoHide(){
    const header = document.querySelector('.site-header') || document.querySelector('header');
    const nav = document.getElementById('primary-nav');
    if (!header) return;
    header.classList.add('transition-transform', 'duration-300', 'will-change-transform');
    let lastY = window.scrollY;
    let ticking = false;
    const threshold = 8; 
    const update = () => {
      ticking = false;
      const y = window.scrollY;
      const goingDown = y > lastY + threshold;
      const goingUp = y < lastY - threshold;
      const navOpen = nav && nav.classList.contains('open');

      if (navOpen || y <= 0 || y < 80) {
        header.classList.remove('-translate-y-full');
        lastY = y;
        return;
      }
      if (goingDown) header.classList.add('-translate-y-full');
      else if (goingUp) header.classList.remove('-translate-y-full');
      lastY = y;
    };
    window.addEventListener('scroll', () => {
      if (!ticking) {
        window.requestAnimationFrame(update);
        ticking = true;
      }
    }, { passive: true });
    update();
  })();

  // Security links
  document.querySelectorAll('a[href^="http"]').forEach((a) => {
    try {
      const url = new URL(a.href, window.location.origin);
      if (url.origin !== window.location.origin) {
        if (!a.hasAttribute('rel')) a.setAttribute('rel', 'noopener noreferrer');
        else if (!/noopener|noreferrer/.test(a.getAttribute('rel'))) a.setAttribute('rel', a.getAttribute('rel') + ' noopener noreferrer');
        a.setAttribute('target', '_blank');
      }
    } catch (e) {}
  });

  function debounce(fn, delay) {
    let timeoutId;
    return (...args) => {
      window.clearTimeout(timeoutId);
      timeoutId = window.setTimeout(() => fn(...args), delay);
    };
  }

  // Publications
  async function renderPublications() {
    const list = document.getElementById('pubs-list');
    if (!list) return;

    const searchInput = document.getElementById('pubs-search');
    const sortBtn = document.getElementById('pubs-sort');
    let pubs = [];
    let sortDesc = true; // default: newest first

    const normalize = (s) => (s || '').toString().toLowerCase();

    const buildItem = (pub) => {
      const authors = Array.isArray(pub.authors) ? pub.authors.join(', ') : pub.authors;
      
      // HTML del Journal destacado (en negrita/azul) dentro de la cita
      const journalHtml = pub.journal 
        ? `<span class="journal-name">${pub.journal}</span>` 
        : '';

      const volumeInfo = [pub.volume && `vol. ${pub.volume}`, pub.issue && `no. ${pub.issue}`].filter(Boolean).join(', ');
      const sourcePart = [journalHtml, volumeInfo].filter(Boolean).join(', ');
      const pagesPart = pub.pages || pub.article ? [pub.pages, pub.article && `article ${pub.article}`].filter(Boolean).join(', ') : null;

      // Construcción de la línea de texto
      const parts = [
        `<strong>${pub.title}</strong>`, 
        authors,
        sourcePart,
        pagesPart,
        pub.year
      ].filter(Boolean);

      const htmlContent = parts.slice(0, -1).join(', ') + ', ' + parts.slice(-1);

      const card = document.createElement('a');
      card.className = 'pub-card';
      card.href = `https://doi.org/${pub.doi}`;
      card.target = '_blank';
      card.rel = 'noopener noreferrer';
      card.setAttribute('aria-label', `Open DOI for ${pub.title}`);
      
      // Insertamos el HTML generado
      card.innerHTML = htmlContent;

      /* * ELIMINADO: Código que añadía el 'chip' (etiqueta superior)
       * El nombre del journal ahora solo aparece integrado en el texto.
       */

      const flashCopied = (button, originalText) => {
        button.classList.add('is-copied');
        button.textContent = 'Copied! ✓';
        window.clearTimeout(button._copyResetTimer);
        button._copyResetTimer = window.setTimeout(() => {
          button.classList.remove('is-copied');
          button.textContent = originalText;
        }, 2000);
      };

      const copyValue = (button, value, originalText) => {
        navigator.clipboard.writeText(value).then(() => {
          flashCopied(button, originalText);
        });
      };

      // Actions row (Botones BibTex/Citation)
      const row = document.createElement('div');
      row.className = 'pub-actions';

      const btnDoi = document.createElement('button');
      btnDoi.type = 'button';
      btnDoi.textContent = 'Copy DOI';
      btnDoi.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        copyValue(btnDoi, pub.doi, 'Copy DOI');
      });
      
      const btnBib = document.createElement('button');
      btnBib.type = 'button';
      btnBib.textContent = 'Copy BibTeX';
      btnBib.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const bib = toBibTeX(pub);
        copyValue(btnBib, bib, 'Copy BibTeX');
      });
      
      const btnCite = document.createElement('button');
      btnCite.type = 'button';
      btnCite.textContent = 'Copy citation';
      btnCite.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const cite = toCitation(pub);
        copyValue(btnCite, cite, 'Copy citation');
      });
      
      row.append(btnDoi, btnBib, btnCite);

      const wrapper = document.createElement('div');
      wrapper.append(card, row);
      return wrapper;
    };

    function toBibTeX(p) {
      const key = (p.authors?.[0] || 'key').split(/[ ,.-]/)[0].toLowerCase() + p.year;
      const author = (p.authors || []).join(' and ');
      const fields = [
        ['author', author], ['title', p.title], ['journal', p.journal],
        p.volume && ['volume', p.volume], p.issue && ['number', p.issue], p.pages && ['pages', p.pages], p.article && ['pages', p.article],
        ['year', String(p.year)], ['doi', p.doi]
      ].filter(Boolean);
      return `@article{${key},\n` + fields.map(([k,v]) => `  ${k} = {${v}}`).join(',\n') + `\n}`;
    }
    
    function toCitation(p) {
      const auth = (p.authors || []).join(', ');
      const volIss = [p.volume && `vol. ${p.volume}`, p.issue && `no. ${p.issue}`].filter(Boolean).join(', ');
      const pg = p.pages || (p.article && `article ${p.article}`) || '';
      return `${auth}. ${p.title}. ${p.journal}${volIss ? ', ' + volIss : ''}${pg ? ', ' + pg : ''}, ${p.year}. https://doi.org/${p.doi}`;
    }

    const render = (items) => {
      list.innerHTML = '';
      const groups = new Map();
      items.forEach((p) => {
        const y = p.year || 'Unknown';
        if (!groups.has(y)) groups.set(y, []);
        groups.get(y).push(p);
      });
      
      const years = Array.from(groups.keys()).sort((a, b) => {
          return sortDesc ? b - a : a - b;
      });

      years.forEach((y, idx) => {
        const det = document.createElement('details');
        det.open = (idx === 0 && sortDesc); 
        const sum = document.createElement('summary');
        sum.textContent = String(y);
        det.appendChild(sum);
        const ul = document.createElement('ul');
        ul.className = 'pubs';
        groups.get(y).forEach((p) => {
          const li = document.createElement('li');
          li.appendChild(buildItem(p));
          ul.appendChild(li);
        });
        det.appendChild(ul);
        list.appendChild(det);
      });
    };

    const apply = () => {
      const q = normalize(searchInput ? searchInput.value : '');
      let filtered = pubs;
      if (q) {
        filtered = pubs.filter((p) => {
          const hay = [p.title, (p.authors || []).join(', '), p.journal, p.doi].map(normalize).join(' ');
          return hay.includes(q);
        });
      }
      filtered.sort((a, b) => (sortDesc ? b.year - a.year : a.year - b.year));
      render(filtered);
    };

    const applyDebounced = debounce(apply, 300);

    try {
      const res = await fetch('assets/docs/publications.json', { cache: 'no-store' });
      if (!res.ok) return; 
      pubs = await res.json();
      apply();
    } catch (e) {
      return;
    }

    if (searchInput) {
      searchInput.addEventListener('input', applyDebounced);
    }
    if (sortBtn) {
      sortBtn.addEventListener('click', () => {
        sortDesc = !sortDesc;
        sortBtn.textContent = sortDesc ? 'Sort by year ↓' : 'Sort by year ↑';
        apply();
      });
      sortBtn.textContent = 'Sort by year ↓';
    }
  }
  renderPublications();

  // Projects toggles
  (function projectToggles(){
    const btnOpen = document.getElementById('proj-expand');
    const btnClose = document.getElementById('proj-collapse');
    if (!btnOpen || !btnClose) return;
    const all = () => Array.from(document.querySelectorAll('#projects details'));
    btnOpen.addEventListener('click', () => all().forEach(d => d.open = true));
    btnClose.addEventListener('click', () => all().forEach(d => d.open = false));
  })();

  // Animate details
  document.querySelectorAll('details').forEach((det) => {
    const content = det.querySelector('.details-content');
    if (!content) return;
    if (!det.open) content.style.height = '0px';
    det.addEventListener('toggle', () => {
      if (det.open) {
        content.style.height = '0px';
        void content.offsetHeight; 
        content.style.height = content.scrollHeight + 'px';
        const onEnd = () => { content.style.height = 'auto'; content.removeEventListener('transitionend', onEnd); };
        content.addEventListener('transitionend', onEnd);
      } else {
        content.style.height = content.scrollHeight + 'px';
        requestAnimationFrame(() => { content.style.height = '0px'; });
      }
    });
  });

  // Team Logic
  document.querySelectorAll('.team-member').forEach((m) => {
      const role = m.getAttribute('data-role');
      if (!role) return;
      let badges = m.querySelector('.badges');
      if (!badges) {
        badges = document.createElement('div');
        badges.className = 'badges';
        const h4 = m.querySelector('h4');
        const roleEl = m.querySelector('.role') || h4;
        roleEl.insertAdjacentElement('afterend', badges);
      }
      const chip = document.createElement('span');
      chip.className = `chip role-chip role-${role}`;
      chip.textContent = (role.toLowerCase() === 'phd') ? 'PhD' : (role.charAt(0).toUpperCase() + role.slice(1));
      badges.appendChild(chip);
  });

  const filterButtons = document.querySelectorAll('.team-controls .pill[data-filter]');
  function applyFilter(filter) {
    const f = filter || 'all';
    document.querySelectorAll('#people .section-subtitle').forEach((heading) => {
      const grid = heading.nextElementSibling;
      if (!grid || !grid.classList.contains('team')) return;
      const items = Array.from(grid.querySelectorAll('.team-member'));
      let any = false;
      items.forEach((item) => {
        const role = item.getAttribute('data-role');
        const show = (f === 'all') || (role === f);
        item.style.display = show ? '' : 'none';
        if (show) any = true;
      });
      const visible = any || f === 'all';
      heading.style.display = visible ? '' : 'none';
      grid.style.display = visible ? '' : 'none';
    });
  }
  
  filterButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      const val = btn.getAttribute('data-filter');
      filterButtons.forEach((b) => { b.classList.remove('active'); });
      btn.classList.add('active');
      applyFilter(val);
    });
  });
  
  const initialActive = document.querySelector('.team-controls .pill[data-filter].active');
  applyFilter(initialActive ? initialActive.getAttribute('data-filter') : 'all');

})();