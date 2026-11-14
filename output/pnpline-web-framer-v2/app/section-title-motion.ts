import gsap from 'gsap';
import {CustomEase} from 'gsap/CustomEase';
import {ScrollTrigger} from 'gsap/ScrollTrigger';
import {SplitText} from 'gsap/SplitText';

gsap.registerPlugin(CustomEase, ScrollTrigger, SplitText);

// Match the hero title's per-character rise and fade.
const riseEase = CustomEase.create('section-title-rise', '0,0,0,1');
const fadeEase = CustomEase.create('section-title-fade', '0.238,0.01,0.044,1');

export function mountSectionTitles() {
  const media = gsap.matchMedia();

  media.add('(prefers-reduced-motion: no-preference)', () => {
    const chapters = gsap.utils.toArray<HTMLElement>(
      '.air-site main :is(#customers, #customers ~ .chapter)',
    );
    const staggeredHeadings = new Set(
      chapters
        .filter((_, index) => index % 2 === 0)
        .map(chapter => chapter.querySelector('.chapter-heading h2, .inquiry-intro h2')),
    );
    const splits: SplitText[] = [];
    const headings = gsap.utils.toArray<HTMLElement>(
      '.air-site main :is(.chapter-heading h2, .b2b-panel > h2, .returns-panel > h2, .inquiry-intro h2)',
    );

    headings.forEach(heading => {
      const subtitle = heading.nextElementSibling;
      const subheading = subtitle?.matches('p') ? subtitle : null;
      const scrollTrigger = {
        trigger: heading,
        endTrigger: subheading ?? heading,
        start: 'top 90%',
        end: 'bottom top',
        toggleActions: 'restart none restart reset',
      };

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
        splits.push(split);
        const timeline = gsap.timeline({scrollTrigger});
        timeline
          .fromTo(split.chars, {y: 32}, {
            y: 0, duration: 0.45, stagger: 0.04, ease: riseEase, clearProps: 'transform',
          }, 0)
          .fromTo(split.chars, {opacity: 0}, {
            opacity: 1, duration: 0.8, stagger: 0.04, ease: fadeEase, clearProps: 'opacity',
          }, 0);
        if (subheading) {
          timeline.fromTo(subheading, {opacity: 0}, {
            opacity: 1, duration: 2, ease: 'power1.out',
          }, 0.12);
        }
        return;
      }

      gsap.fromTo(subheading ? [heading, subheading] : heading, {opacity: 0}, {
        opacity: 1,
        duration: 2,
        stagger: 0.12,
        ease: 'power1.out',
        scrollTrigger,
      });
    });

    const cards = gsap.utils.toArray<HTMLElement>('.air-site main :is(.glass, .quote-inquiry)');
    cards.forEach(card => {
      gsap.from(card, {
        opacity: 0,
        duration: 1,
        ease: 'power1.out',
        scrollTrigger: {
          trigger: card,
          start: 'top 90%',
          end: 'bottom top',
          toggleActions: 'restart none restart reset',
        },
      });
    });

    return () => splits.forEach(split => split.revert());
  });

  return () => media.revert();
}
