/* Progressive enhancements. All research content is already in the HTML. */
(() => {
  'use strict';

  const root = document.documentElement;
  root.classList.add('js');
  const liveRegion = document.getElementById('site-status');
  function announce(message) {
    if (liveRegion) liveRegion.textContent = message;
  }

  const year = document.querySelector('[data-current-year]');
  if (year) year.textContent = String(Math.max(Number(year.textContent), new Date().getFullYear()));

  // Project dates use the visitor's calendar, with both boundary days included.
  // Comparing ISO calendar strings avoids UTC offsets from Date('YYYY-MM-DD').
  const today = new Date();
  const calendarDay = `${String(today.getFullYear()).padStart(4, '0')}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
  const projectLabels = {upcoming: 'Upcoming', ongoing: 'Ongoing', completed: 'Completed'};
  const projectItems = Array.from(document.querySelectorAll('[data-project]'));
  function validCalendarDate(value) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(value || '')) return false;
    const [fullYear, month, day] = value.split('-').map(Number);
    const parsed = new Date(0);
    parsed.setHours(12, 0, 0, 0);
    parsed.setFullYear(fullYear, month - 1, day);
    return fullYear > 0 && parsed.getFullYear() === fullYear && parsed.getMonth() === month - 1 && parsed.getDate() === day;
  }
  projectItems.forEach((item) => {
    const start = item.dataset.startDate;
    const end = item.dataset.endDate;
    let status = item.dataset.status === 'active' ? 'ongoing' : item.dataset.status;
    if (validCalendarDate(start) && validCalendarDate(end) && start <= end) {
      status = calendarDay < start ? 'upcoming' : (calendarDay > end ? 'completed' : 'ongoing');
    }
    if (!projectLabels[status]) return;
    item.dataset.status = status;
    const badge = item.querySelector('[data-project-status]');
    if (badge) {
      Object.keys(projectLabels).concat('active').forEach((key) => badge.classList.remove(`status-${key}`));
      badge.classList.add(`status-${status}`);
      const dot = document.createElement('span');
      dot.setAttribute('aria-hidden', 'true');
      badge.replaceChildren(dot, document.createTextNode(projectLabels[status]));
    }
  });
  const projectById = new Map(projectItems.map((item) => [item.dataset.project, item]));
  const ongoingProjectCount = Array.from(projectById.values()).filter((item) => item.dataset.status === 'ongoing').length;
  document.querySelectorAll('[data-active-project-count]').forEach((element) => {
    element.textContent = String(ongoingProjectCount);
  });
  document.querySelectorAll('[data-current-projects]').forEach((list) => {
    const items = Array.from(list.querySelectorAll('[data-current-project-item]'));
    const ongoing = items.filter((item) => item.dataset.status === 'ongoing');
    const candidates = ongoing.length ? ongoing : [
      ...items.filter((item) => item.dataset.status === 'upcoming'),
      ...items.filter((item) => item.dataset.status === 'completed')
    ];
    const selected = new Set(candidates.slice(0, 3));
    items.forEach((item) => { item.hidden = !selected.has(item); });
  });

  // The menu supports keyboard use, Escape, outside clicks and viewport changes.
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.site-nav');
  const mobile = window.matchMedia('(max-width: 900px)');
  if (toggle && nav) {
    toggle.hidden = false;
    function setMenu(open, returnFocus = false) {
      const isOpen = open && mobile.matches;
      nav.classList.toggle('open', isOpen);
      toggle.setAttribute('aria-expanded', String(isOpen));
      toggle.setAttribute('aria-label', isOpen ? 'Close navigation' : 'Open navigation');
      nav.inert = mobile.matches && !isOpen;
      if (returnFocus && mobile.matches) toggle.focus();
    }
    toggle.addEventListener('click', () => setMenu(toggle.getAttribute('aria-expanded') !== 'true'));
    nav.addEventListener('click', (event) => {
      if (event.target.closest('a')) setMenu(false);
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && nav.classList.contains('open')) setMenu(false, true);
    });
    document.addEventListener('click', (event) => {
      if (!nav.contains(event.target) && !toggle.contains(event.target)) setMenu(false);
    });
    document.addEventListener('focusin', (event) => {
      if (!nav.contains(event.target) && !toggle.contains(event.target)) setMenu(false);
    });
    mobile.addEventListener('change', () => setMenu(false));
    setMenu(false);
  }

  const normalize = (value) => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();
  const directories = document.querySelectorAll('[data-directory]');
  directories.forEach((directory) => {
    const items = Array.from(directory.querySelectorAll('[data-item]'));
    const sections = Array.from(directory.querySelectorAll('[data-section]'));
    const search = directory.querySelector('[data-search]');
    const filters = [
      ['group', directory.querySelector('[data-group-filter]')],
      ['year', directory.querySelector('[data-year-filter]')],
      ['type', directory.querySelector('[data-type-filter]')],
      ['status', directory.querySelector('[data-status-filter]')]
    ].filter(([, control]) => control);
    const sort = directory.querySelector('[data-sort]');
    const noun = {team: 'people', publications: 'publications', projects: 'projects'}[directory.dataset.directory];
    const singular = {team: 'person', publications: 'publication', projects: 'project'}[directory.dataset.directory];
    const index = new Map(items.map((item) => [item, normalize(item.dataset.searchText || '')]));
    const countLabel = (count) => `${count} ${count === 1 ? singular : noun}`;

    function applyFilters() {
      const words = normalize(search ? search.value : '').split(/\s+/).filter(Boolean);
      let total = 0;
      items.forEach((item) => {
        const matchesText = words.every((word) => index.get(item).includes(word));
        const matchesFilters = filters.every(([key, control]) => control.value === 'all' || item.dataset[key] === control.value);
        item.hidden = !matchesText || !matchesFilters;
        if (!item.hidden) total += 1;
      });
      sections.forEach((section) => {
        const count = Array.from(section.querySelectorAll('[data-item]')).filter((item) => !item.hidden).length;
        section.hidden = count === 0;
        const label = section.querySelector('[data-section-count]');
        if (label) label.textContent = countLabel(count);
      });
      const results = directory.querySelector('[data-results]');
      if (results) results.textContent = `${countLabel(total)}${total !== items.length ? ` of ${items.length}` : ''}`;
      const empty = directory.querySelector('[data-empty]');
      if (empty) empty.hidden = total !== 0;
      if (sort) {
        const direction = sort.value === 'oldest' ? 1 : -1;
        const list = directory.querySelector('[data-list]');
        [...sections].sort((a, b) => direction * (Number(a.dataset.year) - Number(b.dataset.year))).forEach((section) => list.appendChild(section));
      }
    }

    if (search) search.addEventListener('input', applyFilters);
    filters.forEach(([, control]) => control.addEventListener('change', applyFilters));
    if (sort) sort.addEventListener('change', applyFilters);
    directory.querySelectorAll('[data-reset]').forEach((button) => {
      button.addEventListener('click', () => {
        if (search) search.value = '';
        filters.forEach(([, control]) => { control.value = 'all'; });
        if (sort) sort.value = 'newest';
        applyFilters();
        if (search) search.focus();
      });
    });
    directory.querySelectorAll('[data-enhancement]').forEach((element) => { element.hidden = false; });
    applyFilters();
  });

  // Rotate every ten seconds while the highlights are visible and unattended.
  // Every record remains readable without JavaScript.
  document.querySelectorAll('[data-featured]').forEach((featured) => {
    const items = Array.from(featured.querySelectorAll('[data-featured-item]'));
    const previous = featured.querySelector('[data-featured-prev]');
    const next = featured.querySelector('[data-featured-next]');
    const status = featured.querySelector('[data-featured-status]');
    const controls = featured.querySelector('[data-featured-controls]');
    const rotation = featured.querySelector('[data-featured-toggle]');
    const progress = featured.querySelector('[data-featured-progress]');
    const progressFill = featured.querySelector('[data-featured-progress-fill]');
    if (items.length < 2 || !previous || !next) return;
    const rotationInterval = 10000;
    const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
    let selected = 0;
    let timer = null;
    let progressFrame = null;
    let progressStarted = null;
    let progressValue = 0;
    let userPaused = false;
    let reducedMotionOverride = false;
    let hovered = false;
    let focused = featured.contains(document.activeElement);
    const bounds = featured.getBoundingClientRect();
    let inView = bounds.bottom > 0 && bounds.top < window.innerHeight;

    function rotationPaused() {
      return userPaused || (motion.matches && !reducedMotionOverride);
    }
    function canRotate() {
      return !rotationPaused() && !hovered && !focused && !document.hidden && inView;
    }
    function paintProgress(value) {
      progressValue = Math.min(1, Math.max(0, value));
      if (progressFill) progressFill.style.transform = `scaleX(${progressValue})`;
      if (progress) {
        progress.setAttribute('aria-valuenow', String(Math.round(progressValue * 100)));
        const seconds = Math.ceil((1 - progressValue) * rotationInterval / 1000);
        const text = canRotate() ? `${seconds} ${seconds === 1 ? 'second' : 'seconds'} until the next highlight` : 'Automatic rotation paused';
        if (progress.getAttribute('aria-valuetext') !== text) progress.setAttribute('aria-valuetext', text);
      }
    }
    function stopProgress() {
      window.cancelAnimationFrame(progressFrame);
      progressFrame = null;
      if (progressStarted !== null) paintProgress((performance.now() - progressStarted) / rotationInterval);
      progressStarted = null;
    }
    function advanceProgress() {
      if (progressStarted === null) return;
      paintProgress((performance.now() - progressStarted) / rotationInterval);
      progressFrame = canRotate() && progressValue < 1 ? window.requestAnimationFrame(advanceProgress) : null;
    }
    function show(index, announceChange = false) {
      stopProgress();
      paintProgress(0);
      selected = (index + items.length) % items.length;
      items.forEach((item, itemIndex) => { item.hidden = itemIndex !== selected; });
      const heading = items[selected].querySelector('h3');
      const title = items[selected].dataset.featuredTitle || (heading ? heading.textContent.trim() : 'Featured research');
      // Announce manual navigation, without interrupting reading during rotation.
      if (status && announceChange) status.textContent = `${selected + 1} of ${items.length} · ${title}`;
    }
    function scheduleRotation() {
      window.clearTimeout(timer);
      timer = null;
      stopProgress();
      if (rotation) {
        const paused = rotationPaused();
        rotation.textContent = paused ? 'Resume' : 'Pause';
        rotation.setAttribute('aria-label', `${paused ? 'Resume' : 'Pause'} automatic research highlights`);
      }
      if (canRotate()) {
        progressStarted = performance.now();
        paintProgress(0);
        if (progressFill) progressFrame = window.requestAnimationFrame(advanceProgress);
        timer = window.setTimeout(() => {
          timer = null;
          if (!canRotate()) return;
          show(selected + 1);
          scheduleRotation();
        }, rotationInterval);
      } else {
        paintProgress(progressValue);
      }
    }
    function navigate(offset) {
      show(selected + offset, true);
      scheduleRotation();
    }
    previous.addEventListener('click', () => navigate(-1));
    next.addEventListener('click', () => navigate(1));
    [previous, next].forEach((button) => {
      button.hidden = false;
      button.addEventListener('keydown', (event) => {
        if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
          event.preventDefault();
          navigate(event.key === 'ArrowLeft' ? -1 : 1);
        }
      });
    });
    if (rotation) {
      rotation.addEventListener('click', () => {
        if (rotationPaused()) {
          userPaused = false;
          reducedMotionOverride = motion.matches;
        } else {
          userPaused = true;
        }
        scheduleRotation();
      });
    }
    featured.addEventListener('pointerenter', (event) => {
      if (event.pointerType === 'touch') return;
      hovered = true;
      scheduleRotation();
    });
    featured.addEventListener('pointerleave', () => {
      hovered = false;
      scheduleRotation();
    });
    featured.addEventListener('focusin', () => {
      focused = true;
      scheduleRotation();
    });
    featured.addEventListener('focusout', (event) => {
      focused = featured.contains(event.relatedTarget);
      scheduleRotation();
    });
    document.addEventListener('visibilitychange', scheduleRotation);
    motion.addEventListener('change', () => {
      reducedMotionOverride = false;
      scheduleRotation();
    });
    if (typeof window.IntersectionObserver === 'function') {
      const observer = new IntersectionObserver(([entry]) => {
        if (inView === entry.isIntersecting) return;
        inView = entry.isIntersecting;
        scheduleRotation();
      });
      observer.observe(featured);
    } else {
      // Older browsers still get timed rotation and the interaction controls.
      inView = true;
    }
    if (controls) controls.hidden = false;
    if (progress) progress.hidden = false;
    show(0);
    scheduleRotation();
  });

  // Citation text stays selectable even if clipboard access is unavailable.
  document.querySelectorAll('[data-copy]').forEach((button) => {
    button.hidden = false;
    button.addEventListener('click', async () => {
      const panel = button.closest('.citation-panel');
      const source = panel.querySelector(`[data-${button.dataset.copy}]`);
      try {
        if (!navigator.clipboard || !navigator.clipboard.writeText) throw new Error('Clipboard unavailable');
        await navigator.clipboard.writeText(source.textContent);
        const original = button.dataset.originalLabel || button.textContent;
        button.dataset.originalLabel = original;
        button.textContent = 'Copied';
        button.classList.add('is-copied');
        announce(`${button.dataset.copy === 'bibtex' ? 'BibTeX' : 'Citation'} copied to clipboard.`);
        window.clearTimeout(button._resetTimer);
        button._resetTimer = window.setTimeout(() => {
          button.textContent = original;
          button.classList.remove('is-copied');
        }, 2000);
      } catch {
        const selection = window.getSelection();
        const range = document.createRange();
        range.selectNodeContents(source);
        selection.removeAllRanges();
        selection.addRange(range);
        announce('Clipboard access is unavailable. The citation is selected; use your device’s copy command.');
      }
    });
  });

  // Landing-page content gently enters once, without a continuous scroll handler.
  // CSS is visible by default; only supported, motion-enabled browsers opt in.
  if (document.body.classList.contains('page-index') && typeof window.IntersectionObserver === 'function') {
    const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (!motion.matches) {
      document.querySelectorAll('[data-scroll-reveal-group]').forEach((group) => {
        Array.from(group.children).filter((item) => !item.hidden).forEach((item, index) => {
          item.setAttribute('data-scroll-reveal', '');
          item.style.setProperty('--reveal-delay', `${Math.min(index, 3) * 60}ms`);
        });
      });
      const targets = Array.from(document.querySelectorAll('[data-scroll-reveal]'));
      const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) reveal(entry.target);
        });
      }, {rootMargin: '0px 0px -24px 0px', threshold: 0});
      function reveal(element, immediate = false) {
        if (immediate) element.classList.add('reveal-immediate');
        element.classList.remove('reveal-pending');
        observer.unobserve(element);
      }
      targets.forEach((element) => {
        // Keep the hero, visible content and restored scroll positions ready.
        if (element.getBoundingClientRect().top >= window.innerHeight) {
          element.classList.add('reveal-pending');
          observer.observe(element);
        }
      });
      document.addEventListener('focusin', (event) => {
        const target = event.target.closest('[data-scroll-reveal]');
        if (target) reveal(target, true);
      });
      motion.addEventListener('change', (event) => {
        if (event.matches) {
          targets.forEach((target) => reveal(target, true));
          observer.disconnect();
        }
      });
    }
  }

  const form = document.getElementById('contact-form');
  if (form) {
    const button = form.querySelector('button[type="submit"]');
    const status = document.getElementById('form-status');
    function showStatus(message, error = false) {
      status.textContent = message;
      status.classList.toggle('is-error', error);
      status.hidden = false;
    }
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      if (button.disabled) return;
      const data = new FormData(form);
      if (!data.get('h-captcha-response')) {
        showStatus('Please complete the verification before sending. If it hasn’t loaded, reload this page and try again.', true);
        status.focus();
        return;
      }
      const originalChildren = Array.from(button.childNodes, (node) => node.cloneNode(true));
      button.disabled = true;
      button.textContent = 'Sending…';
      showStatus('Sending your message…');
      const controller = new AbortController();
      const timeout = window.setTimeout(() => controller.abort(), 20000);
      try {
        const response = await fetch(form.action, {
          method: 'POST',
          headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
          body: JSON.stringify(Object.fromEntries(data)),
          signal: controller.signal
        });
        const result = await response.json();
        if (!response.ok || result.success !== true) throw new Error('Delivery failed');
        form.reset();
        showStatus('Thank you. Your message has been sent to the HWSec-CSIC team.');
        status.focus();
      } catch {
        showStatus('Your message could not be sent. Please try again, or call us at ' + document.querySelector('.footer-phone').textContent + '. Your message is still in the form.', true);
        status.focus();
      } finally {
        window.clearTimeout(timeout);
        if (window.hcaptcha && typeof window.hcaptcha.reset === 'function') window.hcaptcha.reset();
        button.disabled = false;
        button.replaceChildren(...originalChildren);
      }
    });
  }
})();
