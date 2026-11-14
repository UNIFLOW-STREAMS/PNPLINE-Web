const touchInputQuery = '(hover: none) and (pointer: coarse)';
const readingAttribute = 'data-card-in-view';
const enterVisibility = 0.75;
const exitVisibility = 0.60;

export function mountCardReadingState() {
  const main = document.querySelector<HTMLElement>('.air-site main');
  if (!main) return;

  const touchInput = window.matchMedia(touchInputQuery);
  const cards = Array.from(main.querySelectorAll<HTMLElement>('.glass, .quote-inquiry'));
  let activeCards = new Set<HTMLElement>();
  let frame = 0;

  function activate(nextCards: HTMLElement[]) {
    const next = new Set(nextCards);
    for (const card of activeCards) {
      if (!next.has(card)) card.removeAttribute(readingAttribute);
    }
    for (const card of next) {
      if (!activeCards.has(card)) card.setAttribute(readingAttribute, '');
    }
    activeCards = next;
  }

  function update() {
    frame = 0;
    if (!touchInput.matches) {
      activate([]);
      return;
    }

    const viewportHeight = window.innerHeight;
    const center = viewportHeight / 2;
    const retainMargin = viewportHeight * 0.06;
    const candidates: {card: HTMLElement; top: number; distance: number}[] = [];

    for (const card of cards) {
      const {top, bottom, height} = card.getBoundingClientRect();
      if (height <= 0 || bottom <= 0 || top >= viewportHeight) continue;

      // Tall cards can fill the viewport without fitting on screen all at once.
      const visible = Math.min(bottom, viewportHeight) - Math.max(top, 0);
      const visibility = visible / Math.min(height, viewportHeight);
      const wasActive = activeCards.has(card);
      const margin = wasActive ? retainMargin : 0;
      const threshold = wasActive ? exitVisibility : enterVisibility;

      if (visibility < threshold || top > center + margin || bottom < center - margin) continue;

      candidates.push({card, top, distance: Math.abs((top + bottom) / 2 - center)});
    }

    const row = candidates.find(({card}) => activeCards.has(card)) ??
      candidates.sort((a, b) => a.distance - b.distance)[0];
    if (!row) {
      activate([]);
      return;
    }

    // Side-by-side cards share a grid parent and top edge, including fractional layout pixels.
    activate(candidates
      .filter(({card, top}) => card.parentElement === row.card.parentElement && Math.abs(top - row.top) <= 1)
      .map(({card}) => card));
  }

  function schedule() {
    if (!frame) frame = requestAnimationFrame(update);
  }

  function syncInput() {
    if (touchInput.matches) {
      window.addEventListener('scroll', schedule, {passive: true});
      window.addEventListener('resize', schedule);
      resizeObserver.observe(main!);
      for (const card of cards) resizeObserver.observe(card);
      schedule();
    } else {
      window.removeEventListener('scroll', schedule);
      window.removeEventListener('resize', schedule);
      resizeObserver.disconnect();
      activate([]);
    }
  }

  const resizeObserver = new ResizeObserver(schedule);
  touchInput.addEventListener('change', syncInput);
  syncInput();

  return () => {
    touchInput.removeEventListener('change', syncInput);
    window.removeEventListener('scroll', schedule);
    window.removeEventListener('resize', schedule);
    resizeObserver.disconnect();
    cancelAnimationFrame(frame);
    activate([]);
  };
}
