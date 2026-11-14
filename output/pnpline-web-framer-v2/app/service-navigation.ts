/** Align the complete chapter content, excluding its inter-section spacing. */
export function scrollToServiceSection(section: HTMLElement, header: HTMLElement | null) {
  const blocks = Array.from(section.children).filter(
    (element): element is HTMLElement => element instanceof HTMLElement &&
      element.getClientRects().length > 0,
  );
  const bounds = (blocks.length ? blocks : [section]).map(element => element.getBoundingClientRect());
  const top = Math.min(...bounds.map(bound => bound.top)) + window.scrollY;
  const bottom = Math.max(...bounds.map(bound => bound.bottom)) + window.scrollY;
  const height = bottom - top;
  const clearance = (header?.getBoundingClientRect().bottom ?? 0) + 24;
  // Center chapters that fit. Tall chapters start below the bar so their heading
  // and introduction remain readable rather than landing halfway through a card.
  const viewportTop = Math.max(clearance, (window.innerHeight - height) / 2);
  const maxScroll = Math.max(0, document.documentElement.scrollHeight - window.innerHeight);
  const destination = Math.max(0, Math.min(maxScroll, top - viewportTop));

  const previousTabIndex = section.getAttribute('tabindex');
  section.setAttribute('tabindex', '-1');
  section.focus({preventScroll: true});
  section.addEventListener('blur', () => {
    if (previousTabIndex === null) section.removeAttribute('tabindex');
    else section.setAttribute('tabindex', previousTabIndex);
  }, {once: true});
  window.scrollTo({
    top: destination,
    behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth',
  });
}
