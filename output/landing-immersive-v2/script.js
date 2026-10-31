'use strict';

const journey = document.querySelector('.journey');
const pin = document.querySelector('.hero-pin');
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
function selectTab(next, focus = false) {
  tabs.forEach(tab => {
    const selected = tab === next;
    tab.setAttribute('aria-selected', String(selected));
    tab.tabIndex = selected ? 0 : -1;
    document.getElementById(tab.getAttribute('aria-controls')).hidden = !selected;
  });
  if (focus) next.focus();
}
tabs.forEach((tab, index) => {
  tab.addEventListener('click', () => selectTab(tab));
  tab.addEventListener('keydown', event => {
    let next = null;
    if (event.key === 'ArrowRight' || event.key === 'ArrowDown') next = tabs[(index + 1) % tabs.length];
    if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') next = tabs[(index - 1 + tabs.length) % tabs.length];
    if (event.key === 'Home') next = tabs[0];
    if (event.key === 'End') next = tabs[tabs.length - 1];
    if (next) { event.preventDefault(); selectTab(next, true); }
  });
});
const stackedTabs = matchMedia('(max-width: 680px)');
function orientTabs() { document.querySelector('[role="tablist"]').setAttribute('aria-orientation', stackedTabs.matches ? 'vertical' : 'horizontal'); }
stackedTabs.addEventListener('change', orientTabs);
orientTabs();

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
  formStatus.textContent = '设计预览：信息未发送。';
  if (!validateEmail()) email.focus();
});
