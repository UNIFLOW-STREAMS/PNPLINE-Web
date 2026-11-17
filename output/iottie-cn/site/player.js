const action = document.querySelector('#film-action');
const dialog = document.querySelector('#film-dialog');
const video = document.querySelector('#treker-video');
const failure = document.querySelector('#film-failure');
const hero = document.querySelector('#hero-video');
const stage = hero.parentElement;
const motionButton = document.querySelector('#hero-motion');
const motionLabel = document.querySelector('#hero-motion-label');
const heroStatus = document.querySelector('#hero-status');
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');

// Match the poster's selection, including iPads that identify as desktop Safari.
const device = matchMedia('(max-width: 639px)').matches ? 'mobile'
  : matchMedia('(max-width: 1199px), (any-pointer: coarse)').matches ? 'tablet'
  : 'desktop';

let wantsPlayback = !reducedMotion.matches && !navigator.connection?.saveData;
let heroVisible = !('IntersectionObserver' in window);

function renderMotionControl() {
  const playing = !hero.paused;
  motionButton.toggleAttribute('data-playing', playing);
  motionLabel.textContent = playing ? '暂停背景视频' : '播放背景视频';
}

function reportHeroError() {
  wantsPlayback = false;
  stage.classList.remove('has-video');
  heroStatus.textContent = '背景视频暂时无法播放。可重试或观看完整短片。';
  renderMotionControl();
}

function syncHeroPlayback() {
  if (!wantsPlayback || !heroVisible || document.hidden || dialog.open) {
    hero.pause();
    return;
  }
  if (!hero.hasAttribute('src')) hero.src = `assets/treker-${device}.mp4`;
  // Assign the property as well as the content attribute for inline autoplay.
  hero.muted = true;
  hero.play().catch((error) => {
    if (error.name === 'AbortError') return;
    if (hero.error || error.name === 'NotSupportedError') {
      reportHeroError();
    } else {
      // Autoplay restrictions still allow a direct tap on the play control.
      wantsPlayback = false;
      renderMotionControl();
    }
  });
}

hero.addEventListener('play', renderMotionControl);
hero.addEventListener('pause', renderMotionControl);
hero.addEventListener('error', reportHeroError);
hero.addEventListener('playing', () => {
  stage.classList.add('has-video');
  heroStatus.textContent = '';
});
motionButton.addEventListener('click', () => {
  wantsPlayback = hero.paused;
  if (wantsPlayback) {
    heroVisible = true;
    heroStatus.textContent = '';
    if (hero.error) hero.load();
  }
  syncHeroPlayback();
});
motionButton.hidden = false;

function syncMotionPreference() {
  if (reducedMotion.matches) wantsPlayback = false;
  syncHeroPlayback();
}
if (reducedMotion.addEventListener) reducedMotion.addEventListener('change', syncMotionPreference);
else reducedMotion.addListener(syncMotionPreference);
document.addEventListener('visibilitychange', syncHeroPlayback);

if ('IntersectionObserver' in window) {
  new IntersectionObserver(([entry]) => {
    heroVisible = entry.isIntersecting;
    syncHeroPlayback();
  }).observe(document.querySelector('.hero'));
} else {
  syncHeroPlayback();
}

if (typeof dialog?.showModal === 'function' && video && action && failure) {
  action.addEventListener('click', (event) => {
    if (event.ctrlKey || event.metaKey || event.altKey || event.shiftKey) return;
    event.preventDefault();
    dialog.showModal();
    syncHeroPlayback();
    if (!video.hasAttribute('src')) video.src = action.href;
    video.play().catch(() => {
      if (video.error) failure.hidden = false;
    });
  });
  video.addEventListener('error', () => { failure.hidden = false; });
  dialog.addEventListener('close', () => {
    video.pause();
    action.focus();
    syncHeroPlayback();
  });
}
