import gsap from 'gsap';
import {CustomEase} from 'gsap/CustomEase';
import {ScrollTrigger} from 'gsap/ScrollTrigger';
import {SplitText} from 'gsap/SplitText';
import {compactLayoutQuery} from './responsive-layout';

gsap.registerPlugin(CustomEase, ScrollTrigger, SplitText);

// Match the hero title's per-character rise and fade.
const riseEase = CustomEase.create('section-title-rise', '0,0,0,1');
const fadeEase = CustomEase.create('section-title-fade', '0.238,0.01,0.044,1');
const motionQuery = '(prefers-reduced-motion: no-preference)';
const desktopCardQuery = '(width > 1024px) and (hover: hover) and (pointer: fine)';
const cardEntrance = {opacity: 0, duration: 1, ease: 'power1.out'};

function fadeInCard(card: HTMLElement) {
  gsap.from(card, {
    ...cardEntrance,
    scrollTrigger: {
      trigger: card, start: 'top 90%', end: 'bottom top',
      toggleActions: 'play none none none',
      onEnterBack: trigger => trigger.animation?.progress(1),
    },
  });
}

function fadeInCardOnce(card: HTMLElement) {
  // Keep already visible content readable after deep links or layout changes.
  if (card.getBoundingClientRect().top < window.innerHeight || card.contains(document.activeElement)) return;

  const reveal = gsap.from(card, {
    ...cardEntrance,
    clearProps: 'opacity',
    scrollTrigger: {trigger: card, start: 'top 90%', once: true, toggleActions: 'play none play none'},
    onComplete: removeListeners,
  });
  function finish() {
    reveal.progress(1);
  }
  function removeListeners() {
    card.removeEventListener('focusin', finish);
    card.removeEventListener('pointerenter', finish);
  }
  card.addEventListener('focusin', finish);
  card.addEventListener('pointerenter', finish);
  return removeListeners;
}

function revealInViewOnce(
  elements: HTMLElement[],
  seen: WeakSet<HTMLElement>,
  createAnimation: (element: HTMLElement, onComplete: () => void) => gsap.core.Animation,
) {
  const pending = new Map<HTMLElement, gsap.core.Animation>();
  // Disclosures can change positions without scrolling. Observe the elements
  // in their current layout so a reveal cannot start at an old scroll position.
  const observer = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      const element = entry.target as HTMLElement;
      seen.add(element);
      observer.unobserve(element);
      pending.get(element)?.play();
    }
  });

  function finish(event: Event) {
    pending.get(event.currentTarget as HTMLElement)?.progress(1);
  }

  function release(element: HTMLElement) {
    observer.unobserve(element);
    element.removeEventListener('focusin', finish);
    element.removeEventListener('pointerdown', finish);
    pending.delete(element);
  }

  for (const element of elements) {
    if (seen.has(element)) continue;
    if (element.getBoundingClientRect().top < window.innerHeight || element.contains(document.activeElement)) {
      seen.add(element);
      continue;
    }

    const reveal = createAnimation(element, () => {
      seen.add(element);
      release(element);
    });
    pending.set(element, reveal);
    element.addEventListener('focusin', finish);
    element.addEventListener('pointerdown', finish);
    observer.observe(element);
  }

  return () => {
    observer.disconnect();
    for (const element of pending.keys()) release(element);
  };
}

export function mountSectionTitles() {
  const media = gsap.matchMedia();
  const seenCompactHeadings = new WeakSet<HTMLElement>();
  const chapters = gsap.utils.toArray<HTMLElement>(
    '.air-site main :is(#customers, #customers ~ .chapter)',
  );
  const staggeredHeadings = new Set(
    chapters
      .filter((_, index) => index % 2 === 0)
      .map(chapter => chapter.querySelector('.chapter-heading h2, .inquiry-intro h2')),
  );
  const headings = gsap.utils.toArray<HTMLElement>(
    '.air-site main :is(.chapter-heading h2, .b2b-panel > h2, .returns-panel > h2, .inquiry-intro h2)',
  );
  const cards = gsap.utils.toArray<HTMLElement>('.air-site main :is(.glass, .quote-inquiry)');
  const customerGrid = document.querySelector<HTMLElement>('.air-site main #customers .customer-grid');
  const otherCards = cards.filter(card => !card.matches('.customer-card'));

  function createHeadingAnimation(heading: HTMLElement, vars: gsap.TimelineVars) {
    const subtitle = heading.nextElementSibling;
    const subheading = subtitle?.matches('p') ? subtitle : null;

    if (staggeredHeadings.has(heading)) {
      const label = heading.getAttribute('aria-label') ?? heading.innerText.replace(/\s+/g, ' ').trim();
      const split = SplitText.create(heading, {
        type: 'chars',
        tag: 'span',
        charsClass: 'section-title-char',
        smartWrap: document.documentElement.lang.startsWith('en'),
        aria: 'auto',
      });
      heading.setAttribute('aria-label', label);
      const timeline = gsap.timeline(vars);
      timeline
        .fromTo(split.chars, {y: 32}, {
          y: 0, duration: 0.45, stagger: 0.04, ease: riseEase, clearProps: 'transform',
        }, 0)
        .fromTo(split.chars, {opacity: 0}, {
          opacity: 1, duration: 0.8, stagger: 0.04, ease: fadeEase, clearProps: 'opacity',
        }, 0);
      if (subheading) {
        timeline.fromTo(subheading, {opacity: 0}, {
          opacity: 1, duration: 1.3, ease: 'power1.out',
        }, 0.12);
      }
      return {timeline, split};
    }

    const timeline = gsap.timeline(vars);
    timeline.fromTo(heading, {opacity: 0}, {
      opacity: 1,
      duration: 1.25,
      ease: 'power1.out',
    }, 0);
    if (subheading) {
      timeline.fromTo(subheading, {opacity: 0}, {
        opacity: 1,
        duration: 1.3,
        ease: 'power1.out',
      }, 0.12);
    }
    return {timeline};
  }

  function animateScrollHeading(heading: HTMLElement) {
    const subtitle = heading.nextElementSibling;
    return createHeadingAnimation(heading, {scrollTrigger: {
      trigger: heading,
      endTrigger: subtitle?.matches('p') ? subtitle : heading,
      start: 'top 90%',
      end: 'bottom top',
      toggleActions: 'play none none none',
      onEnterBack: trigger => trigger.animation?.progress(1),
    }}).split;
  }

  media.add({motion: motionQuery, compact: compactLayoutQuery}, ({conditions}) => {
    if (!conditions?.motion) return;
    if (!conditions.compact) {
      const splits = headings.map(heading => animateScrollHeading(heading));
      return () => splits.forEach(split => split?.revert());
    }

    // Use current geometry for every compact heading, including those above
    // the first disclosure. Once read, it stays visible through layout changes.
    const splits: SplitText[] = [];
    const cleanup = revealInViewOnce(headings, seenCompactHeadings, (heading, onComplete) => {
      const {timeline, split} = createHeadingAnimation(heading, {paused: true, onComplete});
      if (split) splits.push(split);
      return timeline;
    });
    return () => {
      cleanup();
      splits.forEach(split => split.revert());
    };
  });

  media.add({motion: motionQuery, compact: compactLayoutQuery, desktop: desktopCardQuery}, ({conditions}) => {
    if (!conditions?.motion) return;

    // Compact cards must be readable on the first frame, even after a disclosure
    // shifts the next card into view. CSS still animates the reading surface;
    // fading the whole card would also hide its text, artwork and controls.
    if (conditions.compact) return;

    const desktopTargets = conditions.desktop && customerGrid ? otherCards : cards;
    desktopTargets.forEach(card => {
      fadeInCard(card);
    });
    if (conditions.desktop && customerGrid) return fadeInCardOnce(customerGrid);
  });

  return () => media.revert();
}
