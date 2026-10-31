'use strict';

const journey = document.querySelector('.journey');
const pin = document.querySelector('.hero-pin');
const intro = document.querySelector('.hero-intro');
const video = document.querySelector('.hero-video');
const motionPreference = matchMedia('(prefers-reduced-motion: reduce)');
let desiredProgress = 0;
let lastTarget = -1;
let scheduled = false;
let failed = false;

function journeyLimits() {
  return {
    start: journey.getBoundingClientRect().top + scrollY,
    length: Math.max(1, journey.offsetHeight - pin.offsetHeight),
  };
}

function seekLatest() {
  if (failed || motionPreference.matches || !Number.isFinite(video.duration) || video.seeking) return;
  const target = desiredProgress * Math.max(0, video.duration - 0.001);
  if (Math.abs(target - lastTarget) > 0.012) {
    lastTarget = target;
    video.currentTime = target;
  }
}

function updateJourney() {
  scheduled = false;
  const limits = journeyLimits();
  desiredProgress = motionPreference.matches || failed ? 0 : Math.max(0, Math.min(1, (scrollY - limits.start) / limits.length));
  // Only the surrounding layout expands; video time remains the original linear mapping.
  const introProgress = Math.min(1, desiredProgress / 0.18);
  const introHeight = intro.offsetHeight;
  pin.style.setProperty('--intro-height', `${introHeight}px`);
  pin.style.setProperty('--media-top', `${introHeight * (1 - introProgress)}px`);
  pin.style.setProperty('--intro-shift', `${-introHeight * introProgress}px`);
  pin.style.setProperty('--intro-opacity', String(1 - introProgress));
  // Off-screen links must not remain reachable beneath the fixed header.
  intro.inert = introProgress >= 0.97;
  seekLatest();
}

function scheduleJourney() {
  if (scheduled) return;
  scheduled = true;
  requestAnimationFrame(updateJourney);
}

function setMotionMode() {
  document.body.classList.toggle('is-reduced', motionPreference.matches);
  video.pause();
  lastTarget = -1;
  scheduleJourney();
}

addEventListener('scroll', scheduleJourney, { passive: true });
addEventListener('resize', scheduleJourney);
addEventListener('pageshow', scheduleJourney);
motionPreference.addEventListener('change', setMotionMode);
video.addEventListener('loadedmetadata', () => { video.pause(); lastTarget = -1; updateJourney(); });
video.addEventListener('loadeddata', () => { document.body.classList.add('media-ready'); scheduleJourney(); });
video.addEventListener('seeked', seekLatest);
video.addEventListener('play', () => video.pause());
video.addEventListener('error', () => {
  failed = true;
  video.pause();
  document.body.classList.add('media-failed');
  scheduleJourney();
});
new ResizeObserver(scheduleJourney).observe(intro);
document.fonts.ready.then(scheduleJourney);
setMotionMode();

document.querySelectorAll('a[href^="#"]').forEach(link => {
  link.addEventListener('click', event => {
    const target = document.querySelector(link.getAttribute('href'));
    if (!target) return;
    event.preventDefault();
    target.scrollIntoView({ behavior: 'instant', block: 'start' });
    if (target.hasAttribute('tabindex')) target.focus({ preventScroll: true });
    history.replaceState(null, '', link.getAttribute('href'));
    scheduleJourney();
  });
});

const tabs = [...document.querySelectorAll('[role="tab"]')];
const detail = document.getElementById('service-detail');
const detailTitle = detail.querySelector('.service-detail-title');
const serviceContents = [...detail.querySelectorAll('[data-content]')];
const gridTabs = matchMedia('(max-width: 760px)');

function selectTab(next, focus = false) {
  tabs.forEach(tab => {
    const selected = tab === next;
    tab.setAttribute('aria-selected', String(selected));
    tab.tabIndex = selected ? 0 : -1;
  });
  serviceContents.forEach(content => { content.hidden = content.dataset.content !== next.dataset.service; });
  detail.setAttribute('aria-labelledby', next.id);
  detailTitle.textContent = next.querySelector('.service-tab-label').textContent;
  if (focus) next.focus({ preventScroll: true });
}

tabs.forEach((tab, index) => {
  tab.addEventListener('click', () => {
    selectTab(tab);
    // Native button clicks include Enter/Space activation; arrow navigation stays in the selector.
    if (gridTabs.matches) {
      detail.scrollIntoView({ behavior: 'instant', block: 'start' });
      detail.focus({ preventScroll: true });
    }
  });
  tab.addEventListener('keydown', event => {
    let nextIndex = null;
    if (event.key === 'ArrowRight') nextIndex = (index + 1) % tabs.length;
    if (event.key === 'ArrowLeft') nextIndex = (index - 1 + tabs.length) % tabs.length;
    if (event.key === 'ArrowDown') nextIndex = (index + (gridTabs.matches ? 2 : 1)) % tabs.length;
    if (event.key === 'ArrowUp') nextIndex = (index - (gridTabs.matches ? 2 : 1) + tabs.length) % tabs.length;
    if (event.key === 'Home') nextIndex = 0;
    if (event.key === 'End') nextIndex = tabs.length - 1;
    if (nextIndex !== null) { event.preventDefault(); selectTab(tabs[nextIndex], true); }
  });
});

const form = document.querySelector('.quote-form');
const email = document.getElementById('email');
const emailError = document.getElementById('email-error');
const formStatus = document.querySelector('.form-status');
function validateEmail() {
  const invalid = email.value.trim() !== '' && !email.validity.valid;
  emailError.hidden = !invalid;
  email.setAttribute('aria-invalid', String(invalid));
  return !invalid;
}
email.addEventListener('input', () => { if (email.getAttribute('aria-invalid') === 'true') validateEmail(); });
form.addEventListener('submit', event => {
  event.preventDefault();
  formStatus.textContent = '';
  requestAnimationFrame(() => { formStatus.textContent = '设计预览：信息未发送。'; });
  if (!validateEmail()) email.focus();
});
