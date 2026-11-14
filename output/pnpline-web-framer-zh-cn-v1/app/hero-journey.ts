import { ScrollTrigger } from "gsap/ScrollTrigger";
import { enableHqWorker, fillHqCache, hasStoredHq } from "./hero-hq-cache";
import { buildMapping } from "./hero-mapping";
import config from "./hero-pacing.json";

const mapping = buildMapping(config);
const liteFps = 20;
const seekTolerance = 0.008;

type Framing = "desktop" | "tablet" | "mobile";
type NetworkConnection = EventTarget & {saveData?: boolean};

function frameTime(target: number, fps: number) {
  const frame = Math.floor(target * fps + 1e-6);
  // Seek within the frame to avoid rounding into the preceding frame.
  return frame === 0 ? 0 : (frame + 0.5) / fps;
}

function hasFrame(video: HTMLVideoElement, time: number) {
  return !video.seeking &&
    video.readyState >= HTMLMediaElement.HAVE_CURRENT_DATA &&
    Math.abs(video.currentTime - time) < seekTolerance;
}

function isBuffered(video: HTMLVideoElement, time: number) {
  const ranges = video.buffered;
  for (let index = 0; index < ranges.length; index++) {
    if (ranges.start(index) <= time && time < ranges.end(index)) return true;
  }
  return false;
}

function seek(video: HTMLVideoElement, time: number, retargetWhileSeeking = false) {
  const distance = Math.abs(video.currentTime - time);
  if (video.readyState >= HTMLMediaElement.HAVE_METADATA &&
      (video.seeking ? retargetWhileSeeking && distance >= 0.4 : distance >= seekTolerance)) {
    video.currentTime = time;
  }
}

function unload(video: HTMLVideoElement) {
  video.pause();
  video.removeAttribute("src");
  video.load();
}

export function mountHeroJourney() {
  const track = document.querySelector<HTMLElement>(".landing-film");
  const lite = track?.querySelector<HTMLVideoElement>(".journey-video--lite");
  const high = track?.querySelector<HTMLVideoElement>(".journey-video--hq");
  const screen = track?.querySelector<HTMLElement>(".film-viewport-unit");
  const hold = track?.querySelector<HTMLCanvasElement>(".journey-hold");
  const toggle = document.querySelector<HTMLButtonElement>(".film-motion-toggle");
  if (!track || !lite || !high || !screen || !hold || !toggle) return () => {};

  const connection = (navigator as Navigator & {connection?: NetworkConnection}).connection;
  if (connection?.saveData) return () => {};

  const portrait = window.matchMedia("(orientation: portrait)");
  const compact = window.matchMedia("(max-width: 600px)");
  let framing: Framing | undefined;
  let disposed = false, frozen = false, primed = false, highFailed = false, videoUnavailable = false;
  let targetTime = 0, queued = 0;
  let mediaRequest: AbortController;
  let highAsset = "", workerPlayback = false, localHq = false, highStarted = false;
  let highRetry = 0;

  const keepCurrentFrame = () => {
    if (hold.hasAttribute("data-visible") || track.dataset.heroReady !== "true") return;
    const shown = track.dataset.heroQuality === "hq" ? high : lite;
    if (shown.seeking || shown.readyState < HTMLMediaElement.HAVE_CURRENT_DATA) return;
    const context = hold.getContext("2d");
    if (!context || !shown.videoWidth || !shown.videoHeight) return;
    hold.width = shown.videoWidth;
    hold.height = shown.videoHeight;
    context.drawImage(shown, 0, 0);
    hold.setAttribute("data-visible", "");
  };

  const showFrame = (quality: "lite" | "hq", time: number, fps: number) => {
    track.dataset.heroQuality = quality;
    track.dataset.heroReady = "true";
    track.dataset.heroFrame = String(Math.round(Math.floor(time * fps) * config.fps / fps));
    hold.removeAttribute("data-visible");
  };

  const startLite = () => {
    if (!lite.hasAttribute("src")) lite.src = `/assets/video/hero-scroll-${framing}-lite-v3.mp4`;
  };

  const startHigh = async (fromStorage: boolean, signal: AbortSignal) => {
    highStarted = true;
    const controlled = await enableHqWorker(signal).catch(() => false);
    if (signal.aborted) return;
    workerPlayback = controlled;
    localHq = fromStorage && controlled;
    if (!localHq) startLite();
    high.src = controlled ? `${highAsset}?hero-hq=play` : highAsset;
    if (!controlled || localHq) return;

    const complete = await fillHqCache(highAsset, signal);
    if (signal.aborted) return;
    if (complete) {
      localHq = true;
      if (highFailed) retryHigh();
      queueSeek();
    } else {
      // Keep progressive playback if this browser or server cannot save the complete file.
      keepCurrentFrame();
      workerPlayback = false;
      retryHigh();
    }
  };

  const syncFrame = () => {
    if (disposed || frozen || videoUnavailable || document.hidden) return;
    const highTime = frameTime(targetTime, config.fps);
    if (!highFailed && hasFrame(high, highTime)) {
      showFrame("hq", highTime, config.fps);
      if (localHq && lite.hasAttribute("src")) unload(lite);
      return;
    }
    if (localHq) {
      if (!isBuffered(high, highTime)) keepCurrentFrame();
      seek(high, highTime, true);
      return;
    }
    // Use the matching Lite frame while HQ catches up to the scroll position.
    const liteTime = frameTime(targetTime, liteFps);
    if (!lite.error && hasFrame(lite, liteTime)) {
      showFrame("lite", liteTime, liteFps);

      // Start loading HQ after the first Lite frame is ready to show.
      if (!connection?.saveData && !highStarted) {
        void startHigh(false, mediaRequest.signal);
      }
    } else {
      const shownFrameBuffered = track.dataset.heroQuality === "hq"
        ? !highFailed && isBuffered(high, highTime)
        : !lite.error && isBuffered(lite, liteTime);
      if (!shownFrameBuffered) keepCurrentFrame();
      if (!lite.error) seek(lite, liteTime);
    }
    if (!highFailed) seek(high, highTime, true);
  };

  const queueSeek = () => {
    if (!disposed && !queued) {
      queued = requestAnimationFrame(() => {
        queued = 0;
        syncFrame();
      });
    }
  };

  const selectVideo = () => {
    const next = !portrait.matches ? "desktop" : compact.matches ? "mobile" : "tablet";
    if (framing === next) return;
    keepCurrentFrame();
    mediaRequest?.abort();
    mediaRequest = new AbortController();
    const {signal} = mediaRequest;
    clearTimeout(highRetry);
    framing = next;
    highAsset = `/assets/video/hero-scroll-${next}-hq-v4.mp4`;
    workerPlayback = localHq = highStarted = false;
    highFailed = false;
    videoUnavailable = false;
    primed = false;
    unload(high);
    unload(lite);
    track.dataset.video = "active";
    track.dataset.heroMedia = next;
    track.dataset.heroQuality = "lite";
    if (!hold.hasAttribute("data-visible")) delete track.dataset.heroReady;
    toggle.hidden = false;
    void hasStoredHq(highAsset).then(stored => {
      if (signal.aborted) return;
      if (stored) void startHigh(true, signal);
      else startLite();
    });
    renderJourney(journey.progress);
  };

  const renderJourney = (progress: number) => {
    if (frozen || videoUnavailable) return;
    const frame = mapping.frameAtProgress(progress);
    targetTime = Math.max(0, Math.min(frame / config.fps, config.frameEnd / config.fps));
    track.dataset.heroTargetFrame = frame.toFixed(3);
    track.dataset.heroSection = mapping.sectionAtFrame(frame).id;
    track.style.setProperty("--progress", String(progress));
    track.toggleAttribute("data-final", progress >= 1);
    queueSeek();
  };

  track.dataset.heroVersion = "B-cycles-v002-full-page";
  // Original viewport-based pacing; expanding content never rescales the film.
  const journey = ScrollTrigger.create({
    start: 0, end: () => mapping.total * screen.offsetHeight,
    onUpdate: self => renderJourney(self.progress),
    onRefresh: self => renderJourney(self.progress),
  });

  const setFrozen = () => {
    frozen = !frozen;
    if (frozen) keepCurrentFrame();
    toggle.setAttribute("aria-pressed", String(frozen));
    toggle.setAttribute("title", frozen ? "恢复背景动画" : "暂停背景动画");
    if (!frozen) renderJourney(journey.progress);
  };

  const fallback = () => {
    videoUnavailable = true;
    mediaRequest.abort();
    clearTimeout(highRetry);
    unload(high);
    delete track.dataset.video;
    delete track.dataset.heroReady;
    hold.removeAttribute("data-visible");
    track.removeAttribute("data-final");
    toggle.hidden = true;
  };

  const retryHigh = () => {
    clearTimeout(highRetry);
    if (disposed || videoUnavailable) return;
    highFailed = false;
    high.src = workerPlayback ? `${highAsset}?hero-hq=play` : highAsset;
    queueSeek();
  };

  const onHighError = () => {
    highFailed = true;
    const wasLocal = localHq;
    localHq = false;
    startLite();
    if (lite.error) fallback();
    else {
      if (wasLocal) workerPlayback = false;
      if (workerPlayback || wasLocal) highRetry = window.setTimeout(retryHigh, 3000);
      queueSeek();
    }
  };

  const onLiteError = () => {
    if (highFailed || !high.hasAttribute("src")) fallback();
    else queueSeek();
  };

  const prime = () => {
    if (primed || disposed || videoUnavailable || frozen || lite.error || track.dataset.heroQuality === "hq") return;
    primed = true;
    // User-gesture priming supports later paused seeks on Safari.
    lite.play()?.then(() => {
      if (!disposed) {
        lite.pause();
        queueSeek();
      }
    }).catch(() => { primed = false; });
  };

  const mediaEvents = ["loadedmetadata", "loadeddata", "progress", "canplay", "seeked", "suspend"];
  for (const video of [lite, high]) {
    video.preload = "auto";
    for (const event of mediaEvents) video.addEventListener(event, queueSeek);
  }
  lite.addEventListener("error", onLiteError);
  high.addEventListener("error", onHighError);
  toggle.addEventListener("click", setFrozen);
  document.addEventListener("visibilitychange", queueSeek);
  connection?.addEventListener("change", queueSeek);
  window.addEventListener("pointerdown", prime, {passive:true});
  window.addEventListener("touchstart", prime, {passive:true});
  portrait.addEventListener("change", selectVideo);
  compact.addEventListener("change", selectVideo);
  selectVideo();

  return () => {
    disposed = true;
    mediaRequest?.abort();
    clearTimeout(highRetry);
    journey.kill();
    cancelAnimationFrame(queued);
    toggle.hidden = true;
    toggle.setAttribute("aria-pressed", "false");
    toggle.setAttribute("title", "暂停背景动画");
    toggle.removeEventListener("click", setFrozen);
    portrait.removeEventListener("change", selectVideo);
    compact.removeEventListener("change", selectVideo);
    hold.removeAttribute("data-visible");
    document.removeEventListener("visibilitychange", queueSeek);
    connection?.removeEventListener("change", queueSeek);
    window.removeEventListener("pointerdown", prime);
    window.removeEventListener("touchstart", prime);
    lite.removeEventListener("error", onLiteError);
    high.removeEventListener("error", onHighError);
    for (const video of [lite, high]) {
      for (const event of mediaEvents) video.removeEventListener(event, queueSeek);
      unload(video);
    }
    delete track.dataset.video;
    delete track.dataset.heroReady;
    delete track.dataset.heroQuality;
    track.removeAttribute("data-final");
  };
}
