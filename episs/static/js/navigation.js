// Navegación, accesibilidad y menú. Sin dependencias de los servicios de cálculo.
import { $ } from './dom.js';
import { modules } from './config.js';

export function initShell() {
  const collapse = $('collapseNav');
  collapse.addEventListener('click', () => {
    const compact = document.body.classList.toggle('compact-nav');
    collapse.setAttribute('aria-expanded', String(!compact));
    collapse.setAttribute('aria-label', compact ? 'Expandir menú' : 'Contraer menú');
  });

  new MutationObserver(() => {
    $('form').classList.toggle('has-error', !$('error').hidden);
    if (!$('error').hidden) {
      $('error').setAttribute('tabindex', '-1');
      $('error').focus({
        preventScroll: true,
      });
    }
  }).observe($('error'), {
    attributes: true,
    attributeFilter: ['hidden'],
  });
}

export function initNavigation(onPage) {
  let currentPage;
  const links = [...document.querySelectorAll('[data-page], [data-mode], [data-open]')];
  const pages = new Set(['home', 'info', ...Object.keys(modules)]);

  function display(requested, focus = false) {
    const page = pages.has(requested) ? requested : 'home';
    if (page === currentPage) return;
    currentPage = page;
    const tool = page !== 'home' && page !== 'info';
    $('homeView').hidden = page !== 'home';
    $('infoView').hidden = page !== 'info';
    $('toolView').hidden = !tool;
    onPage(page, tool);

    for (const link of links) {
      const target = link.dataset.page || link.dataset.mode || link.dataset.open;
      if (target === page) link.setAttribute('aria-current', 'page');
      else link.removeAttribute('aria-current');
    }
    const title = page === 'home' ? 'Inicio' : page === 'info' ? 'Información' : modules[page][0];
    $('currentSection').textContent = title;
    document.title = `${title} | Estadística Inferencial UNAJ`;
    if (focus) {
      $(page === 'home' ? 'homeTitle' : page === 'info' ? 'infoTitle' : 'pageTitle').focus({
        preventScroll: true,
      });
      window.scrollTo({
        top: 0,
        behavior: 'instant',
      });
    }
  }

  for (const link of links) {
    link.addEventListener('click', (event) => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      const page = link.dataset.page || link.dataset.mode || link.dataset.open;
      display(page, true);
      if (location.hash !== `#${page}`) location.hash = page;
    });
  }
  window.addEventListener('hashchange', () => display(location.hash.slice(1) || 'home', true));
  display(location.hash.slice(1) || 'home');
}
