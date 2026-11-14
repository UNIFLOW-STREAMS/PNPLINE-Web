import type {MouseEvent} from 'react';

/** Align the visible chapter content without counting the spacing between chapters. */
function scrollToSection(section: HTMLElement, header: HTMLElement | null) {
  const blocks = section.classList.contains('chapter')
    ? Array.from(section.children).filter(element => element.getClientRects().length > 0)
    : [section];
  const bounds = (blocks.length ? blocks : [section]).map(element => element.getBoundingClientRect());
  const top = Math.min(...bounds.map(bound => bound.top)) + window.scrollY;
  const bottom = Math.max(...bounds.map(bound => bound.bottom)) + window.scrollY;
  const height = bottom - top;
  const viewport = window.visualViewport;
  const viewportStart = viewport?.offsetTop ?? 0;
  const viewportHeight = viewport?.height ?? window.innerHeight;
  const clearance = Math.max(viewportStart, header?.getBoundingClientRect().bottom ?? 0) + 24;
  // Center chapters that fit. Tall chapters start below the bar so their heading
  // and introduction remain readable rather than landing halfway through a card.
  const viewportTop = Math.max(clearance, viewportStart + (viewportHeight - height) / 2);

  if (!section.hasAttribute('tabindex')) {
    section.setAttribute('tabindex', '-1');
    section.addEventListener('blur', () => section.removeAttribute('tabindex'), {once: true});
  }
  section.focus({preventScroll: true});
  window.scrollTo({
    top: top - viewportTop,
    behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth',
  });
}

export function navigateToSection(event: MouseEvent<HTMLElement>) {
  if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey ||
    event.shiftKey || event.altKey || !(event.target instanceof Element)) return;

  const link = event.target.closest<HTMLAnchorElement>('a[href^="#"]');
  const landing = event.currentTarget;
  if (!link || !landing.contains(link) || (link.target && link.target !== '_self') ||
    link.hasAttribute('download')) return;

  const section = document.getElementById(link.hash.slice(1));
  if (!section?.matches('main > section.chapter, main section.quote-inquiry') ||
    !landing.contains(section)) return;

  event.preventDefault();
  if (location.hash !== link.hash) history.pushState(history.state, '', link.hash);
  // Measure after any menu onClick handler has closed its panel.
  requestAnimationFrame(() => scrollToSection(section, landing.querySelector('.site-nav')));
}
