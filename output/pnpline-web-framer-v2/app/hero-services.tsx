import {ArrowUpToLine, Pause, Play} from 'lucide-react';

// A decorative film behind the entire page; content stays in normal document flow.
export default function HeroServices() {
  return <>
    <div className="journey-track landing-film" aria-hidden="true">
      <span className="film-viewport-unit"/>
      <div className="journey-screen"><div className="journey-frame">
        <img className="journey-fallback" src="/assets/video/hero-010-poster.webp" width={1920} height={1080} fetchPriority="high" alt=""/>
        <video className="journey-video" muted playsInline preload="none" disablePictureInPicture poster="/assets/video/hero-010-poster.webp"/>
        <img className="journey-final" src="/assets/video/hero-010-last.webp" alt="" width={1920} height={1080}/>
      </div></div>
    </div>
    <div className="film-controls">
      <a className="film-back-to-top" href="#top" aria-label="Back to top" title="Back to top">
        <ArrowUpToLine size={20} aria-hidden="true"/>
      </a>
      <button className="film-motion-toggle" type="button" aria-pressed="false" aria-label="Pause background motion" title="Pause background motion" hidden>
        <Pause className="film-pause-icon" size={20} aria-hidden="true"/>
        <Play className="film-play-icon" size={20} aria-hidden="true"/>
      </button>
    </div>
  </>;
}
