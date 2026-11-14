import gsap from 'gsap';
import {CustomEase} from 'gsap/CustomEase';
import {SplitText} from 'gsap/SplitText';

gsap.registerPlugin(CustomEase, SplitText);

// Figma 27:4211: title 27:4216, GNB 27:4223, CTA 27:4233.
// Adapt the entrance only; the reference's repeating page-exit timeline would
// fight the landing page's existing scroll-controlled film.
const entranceEase = CustomEase.create('hero-entrance', '0.238,0.01,0.044,1');
// Delivery glyphs 27:4364–27:4371: 32px rise, 450ms, 40ms stagger.
const deliveryEase = CustomEase.create('hero-delivery', '0,0,0,1');

export function mountHeroEntrance() {
  const root = document.querySelector<HTMLElement>('.air-site');
  const heroTitle = root?.querySelector<HTMLElement>('.hero-copy > h1');
  if (!root || !heroTitle) return;
  const firstLine = root.querySelector<HTMLElement>('.hero-title-line');
  // The CSS fallback may already have revealed the title before hydration.
  const alreadyVisible = !firstLine || Number(getComputedStyle(firstLine).opacity) > 0;
  const [navigation] = performance.getEntriesByType('navigation') as PerformanceNavigationTiming[];
  const isReload = navigation?.type === 'reload';
  root.dataset.heroEntrance = 'ready';
  // A reload restores the scroll position, which can be at the top with a stale hash.
  const openedAtSectionLink = !isReload && Boolean(location.hash && location.hash !== '#top');
  const openedBelowTop = window.scrollY > 4 || openedAtSectionLink;
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let hasLeftHero = openedBelowTop;
  let previousScrollY = window.scrollY;
  const shouldPlay = !openedBelowTop && (!alreadyVisible || (isReload && !reducedMotion.matches));
  let stopEntrance = shouldPlay ? playHeroEntrance(root) : undefined;

  const replayOnReturn = () => {
    const scrollY = window.scrollY;
    const returning = scrollY < previousScrollY;
    previousScrollY = scrollY;
    // Rearm once the title is out of view, then replay on upward re-entry.
    if (heroTitle.getBoundingClientRect().bottom <= 0) {
      hasLeftHero = true;
      return;
    }
    if (!hasLeftHero || !returning) return;
    hasLeftHero = false;
    if (reducedMotion.matches) return;
    stopEntrance?.();
    stopEntrance = playHeroEntrance(root);
  };
  window.addEventListener('scroll', replayOnReturn, {passive: true});

  return () => {
    window.removeEventListener('scroll', replayOnReturn);
    stopEntrance?.();
    delete root.dataset.heroEntrance;
  };
}

function playHeroEntrance(root: HTMLElement) {
  const media = gsap.matchMedia();
  let played = false;
  media.add({
    full: '(prefers-reduced-motion: no-preference)',
    reduced: '(prefers-reduced-motion: reduce)',
  }, context => {
    // A preference change must reveal the final state, not replay the entrance.
    if (played) return;
    played = true;
    const reduced = context.conditions?.reduced;
    const title = root.querySelectorAll<HTMLElement>('.hero-title-line');
    const nav = root.querySelector<HTMLElement>('.nav-shell');
    const subtitle = root.querySelector<HTMLElement>('.hero-copy > p');
    const buttons = root.querySelectorAll<HTMLElement>('.hero-actions > .button');
    const targets = [nav, ...title, subtitle, ...buttons].filter(
      (element): element is HTMLElement => element !== null,
    );
    const timeline = gsap.timeline({defaults: {ease: entranceEase}});
    const reveal = {opacity: 1, y: 0, scale: 1, clearProps: 'opacity,transform'};
    let split: SplitText | undefined;

    if (reduced) {
      timeline.fromTo(targets, {opacity: 0}, {
        opacity: 1, duration: 0.15, ease: 'power1.out', clearProps: 'opacity',
      });
    } else {
      split = SplitText.create(title, {
        type: 'chars',
        tag: 'span',
        charsClass: 'hero-title-char',
        smartWrap: document.documentElement.lang.startsWith('en'),
        aria: 'auto',
      });
      // Keep natural text and wrapping after the one-time entrance finishes.
      timeline.eventCallback('onComplete', () => split?.revert());
      timeline
        .fromTo(split.chars, {y: 32}, {
          y: 0, duration: 0.45, stagger: 0.04, ease: deliveryEase, clearProps: 'transform',
        }, 0)
        // Use the Figma title fade curve on each glyph as it begins to rise.
        .fromTo(split.chars, {opacity: 0}, {
          opacity: 1, duration: 0.8, stagger: 0.04, clearProps: 'opacity',
        }, 0)
        .fromTo(nav, {opacity: 0, y: -80}, {
          ...reveal, duration: 0.4,
        }, 0.2)
        .fromTo(subtitle, {opacity: 0, y: 12}, {
          ...reveal, duration: 0.3,
        }, 0.3)
        .fromTo(buttons, {opacity: 0, y: 24, scale: 0.86}, {
          ...reveal, duration: 0.5, stagger: 0.1,
        }, 0.4);
    }

    // Navigation/scroll takes priority even during the opening sequence.
    const finish = () => { if (timeline.progress() < 1) timeline.progress(1); };
    let previousScrollY = window.scrollY;
    const onScroll = () => {
      const scrollY = window.scrollY;
      if (scrollY > 4 && scrollY > previousScrollY) finish();
      previousScrollY = scrollY;
    };
    const onVisibility = () => { if (document.hidden) finish(); };
    root.addEventListener('focusin', finish);
    root.addEventListener('pointerdown', finish);
    window.addEventListener('scroll', onScroll, {passive: true});
    document.addEventListener('visibilitychange', onVisibility);
    return () => {
      split?.revert();
      root.removeEventListener('focusin', finish);
      root.removeEventListener('pointerdown', finish);
      window.removeEventListener('scroll', onScroll);
      document.removeEventListener('visibilitychange', onVisibility);
    };
  }, root);

  return () => media.revert();
}

