const assert = require('node:assert/strict');
const {test} = require('node:test');
const {readFileSync} = require('node:fs');
const {join} = require('node:path');
const vm = require('node:vm');
const ts = require('typescript');
const root = join(__dirname, '..');
function compile(file, requireModule) {
  const exports = {};
  const js = ts.transpileModule(readFileSync(join(root, 'app', file), 'utf8'), {
    compilerOptions: {module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020, esModuleInterop: true},
  }).outputText;
  return {exports, js, require: requireModule};
}
// Run the real journey controller against media lifecycle faults. Browser/OS
// behavior is simulated here; live MP4 decoding is checked separately.
async function fixture({cached = false, highLocked = false, highStuck = false} = {}) {
  let now = 0, sequence = 0, journey;
  const timers = new Map(), raf = new Map();
  const later = (callback, delay = 0) => { const id = ++sequence; timers.set(id, {at: now + delay, callback}); return id; };
  class Element extends EventTarget {
    constructor() { super(); this.attributes = new Map(); this.dataset = {}; this.style = {setProperty() {}}; }
    setAttribute(name, value) { this.attributes.set(name, value); }
    removeAttribute(name) { this.attributes.delete(name); }
    hasAttribute(name) { return this.attributes.has(name); }
    toggleAttribute(name, enabled) { enabled ? this.setAttribute(name, '') : this.removeAttribute(name); }
    getContext() { return {drawImage() {}}; }
  }
  class Video extends Element {
    constructor() {
      super(); this.readyState = 0; this.seeking = false; this.paused = true; this.error = null;
      this.position = 0; this.videoWidth = 320; this.videoHeight = 480;
      this.locked = false; this.stuck = false; this.pendingPlay = null; this.loads = 0; this.plays = 0; this.pauses = 0;
      this.buffered = {length: 1, start: () => 0, end: () => 33};
    }
    set src(value) { this.setAttribute('src', value); this.load(); }
    get src() { return this.attributes.get('src') || ''; }
    get currentTime() { return this.position; }
    set currentTime(value) {
      this.position = value; this.seeking = true;
      if (!this.locked && !this.stuck) {
        this.seeking = false;
        queueMicrotask(() => this.dispatchEvent(new Event('seeked')));
      }
    }
    load() {
      this.loads++; this.position = 0; this.seeking = false; this.paused = true;
      this.readyState = this.src ? 4 : 0;
      if (this.src) queueMicrotask(() => this.dispatchEvent(new Event('loadeddata')));
    }
    play() {
      this.plays++; this.paused = false;
      if (this.pendingPlay) return this.pendingPlay;
      this.locked = false; this.seeking = false;
      return Promise.resolve();
    }
    pause() { this.paused = true; this.pauses++; }
  }
  const lite = new Video(), high = new Video(), hold = new Element(), track = new Element(), toggle = new Element();
  high.locked = highLocked; high.stuck = highStuck;
  track.querySelector = name => ({'.journey-video--lite': lite, '.journey-video--hq': high,
    '.film-viewport-unit': {offsetHeight: 700}, '.journey-hold': hold})[name];
  const document = new Element(), window = new Element();
  document.hidden = false;
  document.querySelector = name => ({'.landing-film': track, '.film-motion-toggle': toggle})[name];
  window.matchMedia = () => Object.assign(new Element(), {matches: true});
  window.setTimeout = later;
  const realRequire = name => {
    if (name === 'gsap/ScrollTrigger') return {ScrollTrigger: {create(options) {
      journey = {progress: 0, kill() {}, update() { options.onUpdate(this); }};
      return journey;
    }}};
    if (name === './hero-hq-cache') return {hasStoredHq: async () => cached, enableHqWorker: async () => true, fillHqCache: async () => true};
    if (name === './hero-pacing.json') return require(join(root, 'app/hero-pacing.json'));
    if (name === './hero-mapping') {
      const module = compile('hero-mapping.js', realRequire);
      vm.runInNewContext(module.js, module);
      return module.exports;
    }
    throw Error(name);
  };
  const module = compile('hero-journey.ts', realRequire);
  vm.runInNewContext(module.js, {...module, window, document, navigator: {}, AbortController,
    HTMLMediaElement: {HAVE_METADATA: 1, HAVE_CURRENT_DATA: 2},
    requestAnimationFrame: callback => { const id = ++sequence; raf.set(id, callback); return id; },
    cancelAnimationFrame: id => raf.delete(id), setTimeout: later, clearTimeout: id => timers.delete(id),
    performance: {now: () => now}, console,
  });
  const dispose = module.exports.mountHeroJourney();
  async function settle() {
    for (let count = 0; count < 15; count++) {
      await Promise.resolve();
      const callbacks = [...raf.values()]; raf.clear();
      callbacks.forEach(callback => callback(now));
    }
  }
  async function advance(ms) {
    const end = now + ms;
    for (let count = 0; count < 100; count++) {
      const next = [...timers.entries()].filter(([,t]) => t.at <= end).sort((a,b) => a[1].at - b[1].at)[0];
      if (!next) break;
      now = next[1].at; timers.delete(next[0]); next[1].callback(); await settle();
    }
    now = end; await settle();
  }
  async function scroll(progress) { journey.progress = progress; journey.update(); await settle(); }
  async function visibility(hidden) {
    document.hidden = hidden;
    document.dispatchEvent(new Event('visibilitychange'));
    await settle();
  }
  async function tap() { window.dispatchEvent(new Event('touchend')); await settle(); }
  await settle();
  return {lite, high, track, hold, toggle, window, dispose, settle, advance, scroll, visibility, tap};
}
test('cached HQ that needs activation still follows scrolling', async () => {
  const f = await fixture({cached: true, highLocked: true});
  try {
    await f.tap(); await f.scroll(.4); await f.advance(4000);
    assert.ok(Number(f.track.dataset.heroFrame) > 100, 'Background remains on the initial frame after returning with cached HQ');
    assert.ok(f.high.plays > 0, 'The cached HQ decoder needs its own activation');
    assert.equal(f.track.dataset.heroQuality, 'hq');
  } finally { f.dispose(); }
});
test('a silent HQ seek stall can fall back to a moving Lite frame', async () => {
  const f = await fixture({cached: true, highStuck: true});
  try {
    await f.scroll(.5); await f.advance(5000);
    assert.ok(Number(f.track.dataset.heroFrame) > 200, 'Cached HQ stalls with no error while the background remains frozen');
    assert.equal(f.track.dataset.heroQuality, 'lite');
  } finally { f.dispose(); }
});
test('background / foreground reactivates the currently selected decoder', async () => {
  const f = await fixture();
  try {
    await f.tap(); await f.scroll(.25);
    const before = Number(f.track.dataset.heroFrame);
    await f.visibility(true);
    f.high.locked = f.lite.locked = true;
    await f.visibility(false); await f.tap(); await f.scroll(.6); await f.advance(4000);
    assert.ok(Number(f.track.dataset.heroFrame) > before + 100, 'Background is frozen after returning to the page');
  } finally { f.dispose(); }
});
test('a never-settling play request does not permanently disable recovery', async () => {
  const f = await fixture();
  try {
    f.high.locked = f.lite.locked = true;
    f.high.pendingPlay = f.lite.pendingPlay = new Promise(() => {});
    await f.visibility(true); await f.visibility(false); await f.tap();
    await f.scroll(.5); await f.advance(2500);
    f.high.pendingPlay = f.lite.pendingPlay = null;
    await f.tap(); await f.advance(4000);
    assert.ok(Number(f.track.dataset.heroFrame) > 200, 'A pending play promise locks all later retries');
  } finally { f.dispose(); }
});
test('user pause stays paused across a foreground transition', async () => {
  const f = await fixture();
  try {
    await f.scroll(.2);
    f.toggle.dispatchEvent(new Event('click')); await f.settle();
    const before = f.track.dataset.heroFrame;
    await f.visibility(true); await f.visibility(false); await f.tap(); await f.scroll(.6); await f.advance(4000);
    assert.equal(f.track.dataset.heroFrame, before);
    f.toggle.dispatchEvent(new Event('click')); await f.settle(); await f.advance(4000);
    assert.ok(Number(f.track.dataset.heroFrame) > Number(before));
  } finally { f.dispose(); }
});
test('a permanently stuck decoder is reloaded a bounded number of times', async () => {
  const f = await fixture({cached: true, highStuck: true});
  try {
    await f.scroll(.5); await f.advance(10000);
    const loads = f.high.loads;
    await f.scroll(.6); await f.advance(10000);
    assert.equal(f.high.loads, loads, 'A persistent fault must not cause a reload loop');
    assert.equal(f.track.dataset.heroQuality, 'lite');
  } finally { f.dispose(); }
});
test('late play completion from a suspended page cannot pause the recovered decoder', async () => {
  const f = await fixture();
  try {
    await f.visibility(true);
    let finishOldPlay;
    f.high.pendingPlay = new Promise(resolve => { finishOldPlay = resolve; });
    await f.visibility(false);
    await f.visibility(true);
    f.high.pendingPlay = null;
    await f.visibility(false); await f.scroll(.5);
    const pauses = f.high.pauses;
    finishOldPlay(); await f.settle();
    assert.equal(f.high.pauses, pauses, 'A stale play promise interrupted the current decoder');
    assert.equal(f.track.dataset.heroQuality, 'hq');
  } finally { f.dispose(); }
});
