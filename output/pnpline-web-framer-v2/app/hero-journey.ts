import { ScrollTrigger } from "gsap/ScrollTrigger";
import { buildMapping } from "./hero-mapping";
import config from "./hero-pacing.json";

const mapping = buildMapping(config);

export function mountHeroJourney() {
  const track = document.querySelector<HTMLElement>(".landing-film");
  const video = track?.querySelector<HTMLVideoElement>(".journey-video");
  const screen = track?.querySelector<HTMLElement>(".film-viewport-unit");
  const toggle = document.querySelector<HTMLButtonElement>(".film-motion-toggle");
  if (!track || !video || !screen || !toggle) return () => {};
  const connection = (navigator as Navigator & {connection?: {saveData?: boolean}}).connection;
  if (connection?.saveData) return () => {};
  let disposed = false, failed = false, frozen = false, primed = false;
  let targetTime = 0, queued = 0, frameCallback = 0;

  function seekLatest() {
    if (disposed || failed || frozen || document.hidden || video!.seeking || !Number.isFinite(video!.duration)) return;
    if (Math.abs(video!.currentTime - targetTime) > 1 / (config.fps * 2)) video!.currentTime = targetTime;
  }
  function queueSeek() {
    if (!queued) queued = requestAnimationFrame(() => {queued = 0; seekLatest();});
  }
  function painted(_now: number, metadata: VideoFrameCallbackMetadata) {
    if (disposed) return;
    track!.dataset.heroFrame = String(Math.round(metadata.mediaTime * config.fps));
    ready();
    frameCallback = video!.requestVideoFrameCallback(painted);
  }
  function renderJourney(progress: number) {
    if (frozen) return;
    const frame = mapping.frameAtProgress(progress);
    targetTime = Math.max(0, Math.min(frame / config.fps, config.frameEnd / config.fps));
    track!.dataset.heroTargetFrame = frame.toFixed(3);
    track!.dataset.heroSection = mapping.sectionAtFrame(frame).id;
    track!.style.setProperty("--progress", String(progress));
    track!.toggleAttribute("data-final", progress >= 1);
    queueSeek();
  }
  track.dataset.video = "active";
  track.dataset.heroVersion = "B-cycles-v002-full-page";
  // Original viewport-based pacing; expanding content never rescales the film.
  const journey = ScrollTrigger.create({
    start: 0, end: () => mapping.total * screen.offsetHeight,
    onUpdate: self => renderJourney(self.progress),
    onRefresh: self => renderJourney(self.progress),
  });
  function setFrozen() {
    frozen = !frozen;
    toggle!.setAttribute("aria-pressed", String(frozen));
    const label = frozen ? "Resume background motion" : "Pause background motion";
    toggle!.setAttribute("title", label);
    if (!frozen) renderJourney(journey.progress);
  }
  function fallback() {
    if (disposed || failed) return;
    failed = true;
    journey.kill();
    delete track!.dataset.video;
    track!.removeAttribute("data-final");
    toggle!.hidden = true;
  }
  function ready() {
    if (disposed || failed) return;
    if (video!.readyState >= HTMLMediaElement.HAVE_CURRENT_DATA && !video!.seeking) {
      track!.dataset.heroReady = "true";
    }
    queueSeek();
  }
  function prime() {
    if (primed || disposed || failed || frozen) return;
    primed = true;
    // User-gesture priming supports later paused seeks on Safari.
    video!.play()?.then(() => {if (!disposed) {video!.pause(); queueSeek();}}).catch(() => {primed = false;});
  }
  toggle.hidden = false;
  toggle.addEventListener("click", setFrozen);
  document.addEventListener("visibilitychange", queueSeek);
  window.addEventListener("pointerdown", prime, {passive:true});
  window.addEventListener("touchstart", prime, {passive:true});
  video.addEventListener("loadedmetadata", queueSeek);
  video.addEventListener("loadeddata", ready);
  video.addEventListener("canplay", ready);
  video.addEventListener("seeked", ready);
  video.addEventListener("error", fallback);
  if ("requestVideoFrameCallback" in video) frameCallback = video.requestVideoFrameCallback(painted);
  track.dataset.heroMedia = "1080p";
  video.preload = "auto";
  video.src = "/assets/video/hero-010-new-color-scheme.mp4";
  renderJourney(journey.progress);
  return () => {
    disposed = true;
    journey.kill();
    cancelAnimationFrame(queued);
    if (frameCallback) video.cancelVideoFrameCallback(frameCallback);
    toggle.hidden = true;
    toggle.setAttribute("aria-pressed", "false");
    toggle.setAttribute("title", "Pause background motion");
    toggle.removeEventListener("click", setFrozen);
    document.removeEventListener("visibilitychange", queueSeek);
    window.removeEventListener("pointerdown", prime);
    window.removeEventListener("touchstart", prime);
    video.removeEventListener("loadedmetadata", queueSeek);
    video.removeEventListener("loadeddata", ready);
    video.removeEventListener("canplay", ready);
    video.removeEventListener("seeked", ready);
    video.removeEventListener("error", fallback);
    delete track.dataset.video;
    delete track.dataset.heroReady;
    track.removeAttribute("data-final");
    video.pause(); video.removeAttribute("src"); video.load();
  };
}
