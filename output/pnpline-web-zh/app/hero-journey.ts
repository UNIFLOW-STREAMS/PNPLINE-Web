import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { blindScrollDistance } from "./section-blinds";
import { buildMapping } from "./hero-mapping";
import config from "./hero-pacing.json";

const mapping = buildMapping(config);
const mediaRoot = "/assets/video/hero-b-v002";

// One source film, one approved scroll mapping. No baked retime or extra easing.
export function mountHeroJourney() {
  const track = document.querySelector<HTMLElement>(".journey-track");
  const video = track?.querySelector<HTMLVideoElement>(".journey-video");
  const screen = track?.querySelector<HTMLElement>(".journey-screen");
  const header = document.querySelector<HTMLElement>(".site-header");
  if (!track || !video || !screen || !header) return () => {};
  const connection = (navigator as Navigator & {connection?: {saveData?: boolean}}).connection;
  if (connection?.saveData) return () => {};
  const stops = Array.from(track.querySelectorAll<HTMLButtonElement>(".route-legend button"));
  const labels = track.querySelectorAll<HTMLElement>(".journey-label");
  const canvas = track.querySelector<HTMLCanvasElement>(".journey-ambient");
  const portrait = matchMedia("(max-width:1023px) and (orientation:portrait)");
  const compact = matchMedia("(max-width:1023px), (pointer:coarse)").matches;
  let targetTime = 0, disposed = false, failed = false, primed = false;
  let queued = 0, frameCallback = 0;
  let stageScroll: gsap.core.Tween | undefined;

  function paintAmbient() {
    if (portrait.matches && canvas && video!.readyState >= 2)
      canvas.getContext("2d")?.drawImage(video!, 0, 0, canvas.width, canvas.height);
  }
  function seekLatest() {
    if (disposed || failed || video!.seeking || !Number.isFinite(video!.duration)) return;
    const target = Math.max(0, Math.min(targetTime, config.frameEnd / config.fps));
    if (Math.abs(video!.currentTime - target) > 1 / (config.fps * 2)) video!.currentTime = target;
  }
  function queueSeek() {
    if (!queued) queued = requestAnimationFrame(() => { queued = 0; seekLatest(); });
  }
  function painted(_now: number, metadata: VideoFrameCallbackMetadata) {
    if (disposed) return;
    track!.dataset.heroFrame = String(Math.round(metadata.mediaTime * config.fps));
    track!.dataset.heroReady = "true";
    paintAmbient();
    frameCallback = video!.requestVideoFrameCallback(painted);
  }
  function ready() {
    track!.dataset.heroReady = "true";
    paintAmbient(); queueSeek();
  }
  function renderJourney(progress: number) {
    if (window.scrollY <= blindScrollDistance()) progress = 0;
    const rawFrame = mapping.frameAtProgress(progress);
    // Inverting the mapping can land nanoseconds before an exact stage boundary.
    const roundedFrame = Math.round(rawFrame);
    const frame = Math.abs(rawFrame - roundedFrame) < 1e-6 ? roundedFrame : rawFrame;
    const index = config.sections.findIndex((section, i) =>
      frame >= section.startFrame && (frame < section.endFrame || i === config.sections.length - 1));
    targetTime = frame / config.fps;
    track!.dataset.heroTargetFrame = frame.toFixed(3);
    track!.dataset.heroSection = config.sections[Math.max(0, index)].id;
    track!.style.setProperty("--progress", String(progress));
    labels.forEach((label, i) => label.toggleAttribute("data-current", i === index));
    stops.forEach((stop, i) => i === index ? stop.setAttribute("aria-current", "step") : stop.removeAttribute("aria-current"));
    track!.toggleAttribute("data-final", progress >= 1);
    queueSeek();
  }
  track.dataset.video = "active";
  track.dataset.heroMedia = compact ? "720p" : "1080p";
  track.dataset.heroVersion = "B-cycles-v002";
  function sizeTrack() {
    // svh keeps phone browser-toolbar changes out of the film's scroll distance.
    const h = screen!.offsetHeight;
    track!.style.height = `${blindScrollDistance() + (mapping.total + 1.18) * h}px`;
  }
  sizeTrack();
  ScrollTrigger.addEventListener("refreshInit", sizeTrack);
  const journey = ScrollTrigger.create({trigger: track,
    start: blindScrollDistance,
    end: () => track!.getBoundingClientRect().bottom + window.scrollY - screen!.offsetHeight * 1.18,
    onUpdate: self => renderJourney(self.progress), onRefresh: self => renderJourney(self.progress)});
  function cancelStageScroll() { stageScroll?.kill(); stageScroll = undefined; }
  function interruptKey(event: KeyboardEvent) {
    if (["ArrowUp", "ArrowDown", "PageUp", "PageDown", "Home", "End"].includes(event.key) ||
        (event.key === " " && !(event.target as HTMLElement)?.closest("button"))) cancelStageScroll();
  }
  const stageClicks = stops.map((stop, i) => {
    stop.disabled = false;
    const click = () => {
      cancelStageScroll();
      const progress = mapping.progressAtFrame(config.sections[i].startFrame);
      const destination = Math.ceil(journey.start + progress * (journey.end - journey.start));
      const position = {y: window.scrollY};
      stageScroll = gsap.to(position, {y: destination, duration: Math.min(1.25, .65 + Math.abs(destination-position.y)/innerHeight*.12),
        ease: "power2.inOut", onUpdate: () => {window.scrollTo({top:position.y,behavior:"instant"}); ScrollTrigger.update();},
        onComplete: () => {stageScroll = undefined;}});
    };
    stop.addEventListener("click", click);
    return () => {stop.removeEventListener("click", click); stop.disabled = true;};
  });
  const headerTrigger = ScrollTrigger.create({trigger: track, start: 0,
    end: () => track!.getBoundingClientRect().bottom + window.scrollY - header!.offsetHeight,
    onUpdate: self => header!.toggleAttribute("data-over-film", self.progress < 1),
    onRefresh: self => header!.toggleAttribute("data-over-film", self.progress < 1)});
  function leaveFilm() {
    cancelStageScroll(); stageClicks.forEach(remove => remove());
    journey.kill(); headerTrigger.kill();
    ScrollTrigger.removeEventListener("refreshInit", sizeTrack);
    delete track!.dataset.video;
    header!.removeAttribute("data-over-film");
    track!.removeAttribute("data-final");
    track!.style.removeProperty("height");
    track!.style.removeProperty("--progress");
    labels.forEach(label => label.removeAttribute("data-current"));
    stops.forEach(stop => stop.removeAttribute("aria-current"));
  }
  function fallback() {
    if (failed || disposed) return;
    failed = true; leaveFilm(); ScrollTrigger.refresh();
  }
  function prime() {
    if (primed || disposed || failed) return;
    primed = true;
    // Muted, inline play/pause lets Safari paint later paused seeks.
    const play = video!.play();
    if (play) play.then(() => {if (!disposed) {video!.pause(); queueSeek();}}).catch(() => {primed = false;});
  }
  window.addEventListener("wheel", cancelStageScroll, {passive: true});
  window.addEventListener("touchstart", cancelStageScroll, {passive: true});
  window.addEventListener("pointerdown", cancelStageScroll, {passive: true});
  window.addEventListener("keydown", interruptKey);
  window.addEventListener("pointerdown", prime, {passive: true});
  window.addEventListener("touchstart", prime, {passive: true});
  video.addEventListener("loadedmetadata", queueSeek);
  video.addEventListener("loadeddata", ready);
  video.addEventListener("seeked", queueSeek);
  video.addEventListener("seeked", paintAmbient);
  video.addEventListener("error", fallback);
  portrait.addEventListener("change", paintAmbient);
  if ("requestVideoFrameCallback" in video) frameCallback = video.requestVideoFrameCallback(painted);
  video.preload = "auto";
  video.src = `${mediaRoot}-${compact ? "720p" : "1080p"}.mp4`;
  renderJourney(journey.progress);
  return () => {
    disposed = true; leaveFilm();
    cancelAnimationFrame(queued);
    if (frameCallback) video.cancelVideoFrameCallback(frameCallback);
    window.removeEventListener("wheel", cancelStageScroll);
    window.removeEventListener("touchstart", cancelStageScroll);
    window.removeEventListener("pointerdown", cancelStageScroll);
    window.removeEventListener("keydown", interruptKey);
    window.removeEventListener("pointerdown", prime);
    window.removeEventListener("touchstart", prime);
    portrait.removeEventListener("change", paintAmbient);
    video.removeEventListener("loadedmetadata", queueSeek);
    video.removeEventListener("loadeddata", ready);
    video.removeEventListener("seeked", queueSeek);
    video.removeEventListener("seeked", paintAmbient);
    video.removeEventListener("error", fallback);
    video.pause(); video.removeAttribute("src"); video.load();
  };
}
