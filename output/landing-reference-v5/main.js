'use strict';

(() => {
  const body = document.body;
  const journey = document.querySelector('.journey');
  const pin = document.querySelector('.hero-pin');
  const heroContent = document.querySelector('.hero-content');
  const video = document.querySelector('.hero-video');
  const motionToggle = document.getElementById('reduce-motion');
  const motionPreference = window.matchMedia('(prefers-reduced-motion: reduce)');
  const compactHeight = window.matchMedia('(max-height: 540px)');
  let userReduced = false;
  let mediaFailed = false;
  let inView = false;
  let frameHandle = 0;
  let loadTimer = 0;
  let seekTimer = 0;
  let desiredTime = 0;
  let lastRequestedTime = -1;
  let sourceAttached = false;
  let layoutStaticReason = '';
  let layoutCheckHandle = 0;

  const reduced = () => userReduced || motionPreference.matches;
  const animated = () => !reduced() && !mediaFailed && !layoutStaticReason;

  function stopFrames() {
    if (frameHandle) cancelAnimationFrame(frameHandle);
    frameHandle = 0;
  }

  function clearMediaTimers() {
    clearTimeout(loadTimer);
    clearTimeout(seekTimer);
    loadTimer = 0;
    seekTimer = 0;
  }

  function syncMode() {
    body.classList.toggle('is-reduced', !animated());
    body.classList.toggle('media-failed', mediaFailed);
    body.dataset.motionMode = mediaFailed ? 'fallback' : reduced() ? 'reduced' : layoutStaticReason ? 'static' : 'scroll';
    body.dataset.motionReason = mediaFailed ? 'media-error' : motionPreference.matches ? 'system' : userReduced ? 'user' : layoutStaticReason || 'none';
    if (motionToggle) {
      motionToggle.checked = reduced();
      motionToggle.disabled = motionPreference.matches;
      motionToggle.title = motionPreference.matches ? '已根据系统设置减少动态效果。' : '';
    }
  }

  function showFallback() {
    if (!video || reduced()) return;
    mediaFailed = true;
    video.pause();
    stopFrames();
    clearMediaTimers();
    body.classList.remove('media-ready');
    syncMode();
  }

  function revealCurrentFrame() {
    if (!video || !animated() || video.seeking || video.readyState < 2) return;
    if (Math.abs(video.currentTime - desiredTime) < 0.06) {
      body.classList.add('media-ready');
    }
  }

  function seekLatest() {
    if (!video || !animated() || !sourceAttached || !inView || document.hidden) return;
    if (!Number.isFinite(video.duration) || video.duration <= 0 || video.seeking) return;
    if (Math.abs(desiredTime - lastRequestedTime) < 0.012) {
      revealCurrentFrame();
      return;
    }
    if (Math.abs(video.currentTime - desiredTime) < 0.012) {
      lastRequestedTime = desiredTime;
      revealCurrentFrame();
      return;
    }
    try {
      lastRequestedTime = desiredTime;
      video.currentTime = desiredTime;
      clearTimeout(seekTimer);
      seekTimer = setTimeout(() => {
        if (animated() && video.seeking) showFallback();
      }, 8000);
    } catch {
      showFallback();
    }
  }

  function measureAndSeek() {
    if (!journey || !pin || !video || !animated()) return;
    const top = journey.getBoundingClientRect().top;
    const distance = Math.max(1, journey.offsetHeight - pin.offsetHeight);
    const stickyTop = parseFloat(getComputedStyle(pin).top) || 0;
    const progress = Math.min(1, Math.max(0, (stickyTop - top) / distance));
    journey.dataset.progress = progress.toFixed(4);
    if (Number.isFinite(video.duration) && video.duration > 0) {
      desiredTime = progress * Math.max(0, video.duration - 0.001);
      video.dataset.targetTime = desiredTime.toFixed(4);
      seekLatest();
    }
  }

  function tick() {
    frameHandle = 0;
    if (!animated() || !inView || document.hidden) return;
    measureAndSeek();
    frameHandle = requestAnimationFrame(tick);
  }

  function startFrames() {
    if (!video || !animated() || !inView || document.hidden || frameHandle) return;
    frameHandle = requestAnimationFrame(tick);
  }

  function attachSource() {
    if (!video || !animated() || sourceAttached || !inView) return;
    const source = video.dataset.src;
    if (!source) {
      showFallback();
      return;
    }
    sourceAttached = true;
    lastRequestedTime = -1;
    video.preload = 'auto';
    video.src = source;
    video.load();
    loadTimer = setTimeout(() => {
      if (animated() && video.readyState < 2) showFallback();
    }, 15000);
  }

  function setMotionMode() {
    // Keep a footer control in place when changing the length of the hero.
    const retainTogglePosition = motionToggle && document.activeElement === motionToggle;
    const before = retainTogglePosition ? motionToggle.getBoundingClientRect().top : 0;
    stopFrames();
    clearMediaTimers();
    if (video) {
      video.pause();
      if (!animated()) {
        body.classList.remove('media-ready');
        if (sourceAttached) {
          sourceAttached = false;
          video.removeAttribute('src');
          video.preload = 'none';
          video.load();
        }
      }
    }
    syncMode();
    requestAnimationFrame(() => {
      if (retainTogglePosition) {
        const after = motionToggle.getBoundingClientRect().top;
        window.scrollBy({ top: after - before, behavior: 'instant' });
      }
      if (journey) {
        const rect = journey.getBoundingClientRect();
        inView = rect.bottom > 0 && rect.top < innerHeight;
      }
      attachSource();
      measureAndSeek();
      startFrames();
    });
  }

  function checkLayoutMode() {
    layoutCheckHandle = 0;
    if (!journey || !pin || !heroContent) return;
    const headerHeight = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--header')) || 0;
    const availableHeight = Math.max(0, innerHeight - headerHeight);
    // The content's own height stays natural even when the sticky parent is fixed.
    const contentHeight = Math.max(heroContent.scrollHeight, heroContent.getBoundingClientRect().height);
    const nextReason = compactHeight.matches ? 'compact-height' : contentHeight > availableHeight + 2 ? 'content-overflow' : '';
    if (nextReason !== layoutStaticReason) {
      layoutStaticReason = nextReason;
      setMotionMode();
    } else {
      measureAndSeek();
      startFrames();
    }
  }

  function scheduleLayoutCheck() {
    if (!layoutCheckHandle) layoutCheckHandle = requestAnimationFrame(checkLayoutMode);
  }

  if (motionToggle) {
    motionToggle.addEventListener('change', () => {
      userReduced = motionToggle.checked;
      setMotionMode();
    });
  }
  motionPreference.addEventListener('change', setMotionMode);
  compactHeight.addEventListener('change', scheduleLayoutCheck);

  if (journey && pin && video) {
    video.addEventListener('play', () => video.pause());
    video.addEventListener('loadedmetadata', () => {
      if (!animated() || !sourceAttached) return;
      if (!Number.isFinite(video.duration) || video.duration <= 0) {
        showFallback();
        return;
      }
      video.pause();
      lastRequestedTime = -1;
      measureAndSeek();
      startFrames();
    });
    video.addEventListener('loadeddata', () => {
      clearTimeout(loadTimer);
      loadTimer = 0;
      measureAndSeek();
      revealCurrentFrame();
    });
    video.addEventListener('seeked', () => {
      clearTimeout(seekTimer);
      seekTimer = 0;
      revealCurrentFrame();
      seekLatest();
    });
    video.addEventListener('error', () => {
      if (sourceAttached && animated()) showFallback();
    });
    new IntersectionObserver(entries => {
      inView = entries[0].isIntersecting;
      if (inView) {
        attachSource();
        measureAndSeek();
        startFrames();
      } else {
        stopFrames();
      }
    }).observe(journey);
    const layoutObserver = new ResizeObserver(scheduleLayoutCheck);
    layoutObserver.observe(pin);
    if (heroContent) layoutObserver.observe(heroContent);
    window.addEventListener('resize', scheduleLayoutCheck);
    window.addEventListener('pageshow', () => {
      measureAndSeek();
      startFrames();
    });
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        video.pause();
        stopFrames();
      } else {
        measureAndSeek();
        startFrames();
      }
    });
    if (document.fonts) document.fonts.ready.then(scheduleLayoutCheck);
  }
  // Establish static fallback before an IntersectionObserver can attach media.
  checkLayoutMode();
  setMotionMode();

  const menuButton = document.querySelector('.menu-toggle');
  const menu = document.getElementById('mobile-menu');
  const compactNavigation = window.matchMedia('(max-width: 1023px)');

  function setMenu(open, restoreFocus = false) {
    if (!menuButton || !menu) return;
    menu.hidden = !open;
    menuButton.setAttribute('aria-expanded', String(open));
    menuButton.setAttribute('aria-label', open ? '关闭菜单' : '打开菜单');
    body.classList.toggle('menu-open', open);
    if (restoreFocus) menuButton.focus();
  }

  if (menuButton && menu) {
    setMenu(false);
    menuButton.addEventListener('click', () => setMenu(menu.hidden));
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && !menu.hidden) setMenu(false, true);
    });
    document.addEventListener('click', event => {
      if (!menu.hidden && !menu.contains(event.target) && !menuButton.contains(event.target)) {
        setMenu(false);
      }
    });
    document.addEventListener('focusin', event => {
      if (!menu.hidden && !menu.contains(event.target) && !menuButton.contains(event.target)) {
        setMenu(false);
      }
    });
    compactNavigation.addEventListener('change', () => {
      if (!compactNavigation.matches) setMenu(false);
    });
  }

  document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', event => {
      const hash = link.getAttribute('href');
      if (!hash || hash === '#') return;
      let target;
      try { target = document.getElementById(decodeURIComponent(hash.slice(1))); } catch { return; }
      if (!target) return;
      event.preventDefault();
      setMenu(false);
      target.scrollIntoView({ behavior: 'instant', block: 'start' });
      if (!target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
      target.focus({ preventScroll: true });
      history.replaceState(null, '', hash);
      measureAndSeek();
    });
  });

  const form = document.getElementById('quote-form');
  if (form) {
    const email = document.getElementById('email');
    const consent = document.getElementById('consent');
    const emailError = document.getElementById('email-error');
    const consentError = document.getElementById('consent-error');
    const submitButton = document.getElementById('quote-submit');
    const status = form.querySelector('.form-status') || document.querySelector('.form-status');

    function showError(field, message, invalid, text) {
      if (field) field.setAttribute('aria-invalid', String(invalid));
      if (message) {
        message.hidden = !invalid;
        if (text) message.textContent = text;
      }
    }

    function previewQuote(event) {
      if (event) event.preventDefault();
      if (status) status.textContent = '设计预览：信息未发送。';
      const emailInvalid = email && email.value.trim() !== '' && !email.validity.valid;
      const consentMissing = consent && !consent.checked;
      showError(email, emailError, emailInvalid, '请填写有效的联系邮箱。');
      showError(consent, consentError, consentMissing, '请阅读隐私政策并确认后提交。');
      if (emailInvalid) email.focus();
      else if (consentMissing) consent.focus();
    }

    // This preview has no endpoint, fetch, persistence, or successful-receipt state.
    form.addEventListener('submit', previewQuote);
    if (submitButton) submitButton.addEventListener('click', previewQuote);
    if (email) email.addEventListener('input', () => {
      if (email.getAttribute('aria-invalid') === 'true') {
        showError(email, emailError, email.value.trim() !== '' && !email.validity.valid);
      }
    });
    if (consent) consent.addEventListener('change', () => {
      if (consent.checked) showError(consent, consentError, false);
    });
  }
})();
