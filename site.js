(() => {
  const requested = new URLSearchParams(location.search).get('lang');
  if (['en', 'de', 'fr', 'it'].includes(requested) && requested !== document.documentElement.lang) {
    const alternate = document.querySelector(`link[rel="alternate"][hreflang="${requested}"]`);
    if (alternate) {
      const params = new URLSearchParams(location.search); params.delete('lang');
      const query = params.toString();
      location.replace(new URL(alternate.href).pathname + (query ? '?' + query : '') + location.hash);
      return;
    }
  }
  const menu = document.querySelector('.nav-toggle');
  const nav = document.querySelector('#main-nav');
  if (menu && nav) {
    menu.addEventListener('click', () => {
      const open = menu.getAttribute('aria-expanded') !== 'true';
      menu.setAttribute('aria-expanded', String(open));
      nav.classList.toggle('is-open', open);
    });
    nav.addEventListener('click', e => {
      if (e.target.closest('a')) { nav.classList.remove('is-open'); menu.setAttribute('aria-expanded', 'false'); }
    });
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') { nav.classList.remove('is-open'); menu.setAttribute('aria-expanded', 'false'); }
    });
  }
  document.querySelectorAll('.faq-q').forEach(button => {
    button.setAttribute('type', 'button');
    button.setAttribute('aria-expanded', 'false');
    button.addEventListener('click', () => {
      const item = button.closest('.faq-item');
      const open = button.getAttribute('aria-expanded') !== 'true';
      button.setAttribute('aria-expanded', String(open));
      item.classList.toggle('open', open);
      const answer = item.querySelector('.faq-a');
      if (answer) answer.hidden = !open;
    });
    const answer = button.closest('.faq-item').querySelector('.faq-a');
    if (answer) answer.hidden = true;
  });
  const toc = document.querySelector('#tocToggle');
  if (toc) toc.addEventListener('click', () => {
    const root = document.querySelector('#toc');
    const open = root.dataset.open !== 'true';
    root.dataset.open = String(open); toc.setAttribute('aria-expanded', String(open));
  });
  const search = document.querySelector('#blog-search');
  const tag = new URLSearchParams(location.search).get('tag');
  if (search) {
    const cards = [...document.querySelectorAll('.blog-grid-card')];
    const count = document.querySelector('#blog-count');
    const empty = document.querySelector('#blog-empty');
    const filter = () => {
      const q = search.value.trim().toLocaleLowerCase(); let visible = 0;
      cards.forEach(card => {
        const match = (!tag || (card.dataset.tags || '').split(' ').includes(tag)) && (!q || card.textContent.toLocaleLowerCase().includes(q));
        card.hidden = !match; if (match) visible++;
      });
      count.textContent = String(visible); empty.hidden = visible > 0;
    };
    search.addEventListener('input', filter); filter();
  }
  const panel = document.querySelector('#cookie-panel');
  const loadAnalytics = () => {
    if (document.querySelector('[data-analytics]')) return;
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({'gtm.start': Date.now(), event: 'gtm.js'});
    const script = document.createElement('script'); script.async = true;
    script.src = 'https://www.googletagmanager.com/gtm.js?id=GTM-58NQ8LPN';
    script.dataset.analytics = 'true'; document.head.appendChild(script);
  };
  let consent = null;
  try { consent = localStorage.getItem('sw-analytics-consent'); } catch (_) {}
  if (panel) panel.hidden = consent !== null;
  if (consent === 'yes') loadAnalytics();
  document.querySelectorAll('[data-consent]').forEach(button => button.addEventListener('click', () => {
    const value = button.dataset.consent;
    try { localStorage.setItem('sw-analytics-consent', value); } catch (_) {}
    panel.hidden = true;
    if (value === 'yes') loadAnalytics();
    if (value === 'no' && document.querySelector('[data-analytics]')) {
      window['ga-disable-G-HHTMBHS0F3'] = true;
      location.reload();
    }
  }));
  document.querySelectorAll('[data-cookie-settings]').forEach(button => button.addEventListener('click', () => { panel.hidden = false; panel.querySelector('button').focus(); }));
})();
