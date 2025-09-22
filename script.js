// Minimal interactions: mobile nav and reveal-on-scroll

(function() {
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.site-nav');
  const links = document.querySelectorAll('.site-nav a');
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

  // Smooth scroll for same-page anchors (respects prefers-reduced-motion)
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

  // Reveal on scroll using IntersectionObserver
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
    // Fallback
    els.forEach((el) => el.classList.add('revealed'));
  }

  // Scroll spy: highlight active section link in nav
  const sections = document.querySelectorAll('section[id]');
  const navLinks = Array.from(document.querySelectorAll('.site-nav a[href^="#"]'));
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

  // Back to top button
  const toTop = document.querySelector('.to-top');
  if (toTop) {
    const onScroll = () => {
      if (window.scrollY > 320) {
        toTop.hidden = false;
      } else {
        toTop.hidden = true;
      }
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    toTop.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: prefersReduced ? 'auto' : 'smooth' });
    });
    onScroll();
  }

  // Top progress bar
  const progressBar = document.querySelector('.progress-bar');
  if (progressBar) {
    const updateProgress = () => {
      const scrollTop = window.scrollY || document.documentElement.scrollTop;
      const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
      const pct = Math.max(0, Math.min(1, height ? scrollTop / height : 0));
      progressBar.style.width = (pct * 100).toFixed(2) + '%';
    };
    window.addEventListener('scroll', updateProgress, { passive: true });
    window.addEventListener('resize', updateProgress);
    updateProgress();
  }

  // Auto-hide/reveal header on scroll direction
  (function headerAutoHide(){
    const header = document.querySelector('.site-header');
    const nav = document.getElementById('primary-nav');
    const bar = document.getElementById('newsbar');
    if (!header) return;
    let lastY = window.scrollY;
    let ticking = false;
    const threshold = 8; // px
    const update = () => {
      ticking = false;
      const y = window.scrollY;
      const goingDown = y > lastY + threshold;
      const goingUp = y < lastY - threshold;
      const navOpen = nav && nav.classList.contains('open');

      // Always show when near the very top or if mobile nav is open
      if (navOpen || y <= 0 || y < 80) {
        header.classList.remove('hidden');
        if (bar) bar.classList.remove('hidden');
        lastY = y;
        return;
      }

      if (goingDown) {
        header.classList.add('hidden');
        if (bar) bar.classList.add('hidden');
      } else if (goingUp) {
        header.classList.remove('hidden');
        if (bar) bar.classList.remove('hidden');
      }
      lastY = y;
    };
    window.addEventListener('scroll', () => {
      if (!ticking) {
        window.requestAnimationFrame(update);
        ticking = true;
      }
    }, { passive: true });
    // Initialize state on load
    update();
  })();

  // Newsletter bar (dismissible)
  const newsbar = document.getElementById('newsbar');
  const newsClose = document.getElementById('newsbar-close');
  if (newsbar && newsClose) {
    const key = 'hwsec-newsbar-dismissed-v1';
    if (!localStorage.getItem(key)) newsbar.hidden = false;
    newsClose.addEventListener('click', () => { localStorage.setItem(key, '1'); newsbar.hidden = true; });
  }

  // Security: harden external links (noopener, noreferrer)
  document.querySelectorAll('a[href^="http"]').forEach((a) => {
    try {
      const url = new URL(a.href, window.location.origin);
      if (url.origin !== window.location.origin) {
        if (!a.hasAttribute('rel')) a.setAttribute('rel', 'noopener noreferrer');
        else if (!/noopener|noreferrer/.test(a.getAttribute('rel'))) a.setAttribute('rel', a.getAttribute('rel') + ' noopener noreferrer');
        a.setAttribute('target', '_blank');
      }
    } catch (e) { /* ignore invalid URLs */ }
  });

  // Publications: fetch, render as clickable cards, search, sort
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
      const parts = [
        pub.title,
        authors,
        [pub.journal, pub.volume && `vol. ${pub.volume}`, pub.issue && `no. ${pub.issue}`].filter(Boolean).join(', '),
        pub.pages || pub.article ? [pub.pages, pub.article && `article ${pub.article}`].filter(Boolean).join(', ') : null,
        pub.year
      ].filter(Boolean);
      const text = parts.slice(0, -1).join(', ') + ', ' + parts.slice(-1);

      // Make the whole card an anchor to DOI
      const card = document.createElement('a');
      card.className = 'pub-card';
      card.href = `https://doi.org/${pub.doi}`;
      card.target = '_blank';
      card.rel = 'noopener noreferrer';
      card.setAttribute('aria-label', `Open DOI for ${pub.title}`);
      card.textContent = text;

      // Journal chip
      const chip = document.createElement('span');
      chip.className = 'chip journal';
      chip.textContent = pub.journal;
      card.prepend(chip);

      // Actions row
      const row = document.createElement('div');
      row.className = 'pub-actions';
      const btnBib = document.createElement('button');
      btnBib.type = 'button'; btnBib.className = 'pill'; btnBib.textContent = 'Copy BibTeX';
      btnBib.addEventListener('click', (e) => {
        e.preventDefault(); e.stopPropagation();
        const bib = toBibTeX(pub);
        navigator.clipboard.writeText(bib).then(() => { btnBib.textContent = 'Copied!'; setTimeout(() => btnBib.textContent = 'Copy BibTeX', 1200); });
      });
      const btnCite = document.createElement('button');
      btnCite.type = 'button'; btnCite.className = 'pill'; btnCite.textContent = 'Copy citation';
      btnCite.addEventListener('click', (e) => {
        e.preventDefault(); e.stopPropagation();
        const cite = toCitation(pub);
        navigator.clipboard.writeText(cite).then(() => { btnCite.textContent = 'Copied!'; setTimeout(() => btnCite.textContent = 'Copy citation', 1200); });
      });
      row.append(btnBib, btnCite);

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
      // Group by year desc
      const groups = new Map();
      items.forEach((p) => {
        const y = p.year || 'Unknown';
        if (!groups.has(y)) groups.set(y, []);
        groups.get(y).push(p);
      });
      const years = Array.from(groups.keys()).sort((a, b) => b - a);
      years.forEach((y, idx) => {
        const det = document.createElement('details');
        det.open = idx === 0; // newest year open
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

    try {
      const res = await fetch('data/publications.json', { cache: 'no-store' });
      if (!res.ok) return; // keep fallback
      pubs = await res.json();
      apply();
    } catch (e) {
      // leave fallback
      return;
    }

    if (searchInput) {
      searchInput.addEventListener('input', () => apply());
    }
    if (sortBtn) {
      sortBtn.addEventListener('click', () => {
        sortDesc = !sortDesc;
        sortBtn.setAttribute('aria-pressed', String(sortDesc));
        sortBtn.textContent = sortDesc ? 'Sort by year ↓' : 'Sort by year ↑';
        apply();
      });
      // Initialize label
      sortBtn.textContent = 'Sort by year ↓';
      sortBtn.setAttribute('aria-pressed', 'true');
    }
  }
  renderPublications();

  // Projects expand/collapse all
  (function projectToggles(){
    const btnOpen = document.getElementById('proj-expand');
    const btnClose = document.getElementById('proj-collapse');
    if (!btnOpen || !btnClose) return;
    const all = () => Array.from(document.querySelectorAll('#projects details'));
    btnOpen.addEventListener('click', () => all().forEach(d => d.open = true));
    btnClose.addEventListener('click', () => all().forEach(d => d.open = false));
  })();

  

  // Animate <details> open/close with height transitions
  document.querySelectorAll('details').forEach((det) => {
    const content = det.querySelector('.details-content');
    if (!content) return;
    if (!det.open) content.style.height = '0px';
    det.addEventListener('toggle', () => {
      const isOpen = det.open;
      if (isOpen) {
        content.style.height = '0px';
        // Force reflow
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

  // Team filters and list view toggle
  const teamGrids = document.querySelectorAll('.team');
  const filterButtons = document.querySelectorAll('.team-controls .pill[data-filter]');

  // Inject role chips on person cards
  (function addRoleChips(){
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
  })();

  // Initialize origin mapping for members and ensure grids have ids
  (function initTeamOrigins(){
    let i = 0;
    document.querySelectorAll('#people .team').forEach((grid) => {
      if (!grid.id) { grid.id = `team-grid-${++i}`; }
      grid.querySelectorAll('.team-member').forEach((m) => {
        if (!m.dataset.origin) m.dataset.origin = grid.id;
      });
    });
  })();
  function applyFilter(filter) {
    const f = filter || 'all';
    // Show subsection(s) normally in list view only
    document.querySelectorAll('#people .section-subtitle').forEach((heading) => {
      const grid = heading.nextElementSibling;
      if (!grid || !grid.classList.contains('team')) return;
      const items = Array.from(grid.querySelectorAll('.team-member'));
      let any = false;
      items.forEach((item) => {
        const role = item.getAttribute('data-role');
        const show = (f === 'all') || (role === f);
        if (show) {
          any = true;
          item.classList.remove('hidden');
          item.classList.add('show');
          item.style.display = '';
        } else {
          item.classList.remove('show');
          item.classList.add('hidden');
          setTimeout(() => { item.style.display = 'none'; }, 150);
        }
      });
      const visible = any || f === 'all';
      heading.style.display = visible ? '' : 'none';
      grid.style.display = visible ? '' : 'none';
    });
  }
  filterButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      const val = btn.getAttribute('data-filter');
      filterButtons.forEach((b) => { b.classList.remove('active'); b.setAttribute('aria-pressed', 'false'); });
      btn.classList.add('active');
      btn.setAttribute('aria-pressed', 'true');
      applyFilter(val);
    });
  });
  // Force list view only
  teamGrids.forEach((grid) => grid.classList.add('list-view'));

  // Initialize filter state on load
  const initialActive = document.querySelector('.team-controls .pill[data-filter].active');
  applyFilter(initialActive ? initialActive.getAttribute('data-filter') : 'all');

  // Removed grid packing as grid view is disabled
})();
