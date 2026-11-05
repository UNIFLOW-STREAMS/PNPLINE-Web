"""Stage/apply the same versioned film and approved pacing to both existing apps."""
from pathlib import Path
import argparse, hashlib, json, shutil

ROOT = Path(__file__).resolve().parents[1]
REPO = Path('F:/pnpline-landing')
SITES = {
    'en': Path('C:/Users/KIM TAEHYUNG/.codex/visualizations/2026/11/01/01a19616-7090-7b72-86b1-f85ae4da029a/pnpline-web'),
    'zh': REPO/'output/pnpline-web-zh',
}
LABELS = {
    'en': ['China loading','China departure','Ocean crossing','US unloading','Warehouse arrival','Pick & pack','US dispatch'],
    'zh': ['中国装货','中国起运','跨洋运输','美国卸货','货车入仓','拣货包装','美国配送'],
}
CAPTIONS = {
    'en': ['Container loading in China','China city and port departure','Crossing the Pacific','Unloading at the US port','Truck arrival at the warehouse','Warehouse picking and packing','US dispatch and delivery'],
    'zh': ['中国港口集装箱装货','中国城市与港口起运','跨越太平洋','美国港口卸货','货车抵达美国仓库','仓库拣货与包装','美国出库与配送'],
}

def stage(lang, site):
    out=ROOT/'site-stage'/lang
    (out/'app').mkdir(parents=True,exist_ok=True)
    if not (out/'package.json').exists():
        shutil.copytree(site/'app',out/'app',dirs_exist_ok=True)
        for name in ('package.json','tsconfig.json','next-env.d.ts','postcss.config.mjs'):
            if (site/name).exists():shutil.copy2(site/name,out/name)
    motion=(site/'app/motion.tsx').read_text(encoding='utf-8')
    if 'mountHeroJourney' not in motion:
        motion=motion.replace('import { blindScrollDistance } from "./section-blinds";', 'import { mountHeroJourney } from "./hero-journey";')
        start=motion.index('      const track = document.querySelector<HTMLElement>(".journey-track")!;')
        end=motion.index('      gsap.utils.toArray<HTMLElement>',start)
        motion=motion[:start]+'      const cleanupJourney = mountHeroJourney();\n'+motion[end:]
        start=motion.index('      return () => {\n        leaveFilm();')
        end=motion.index('    });\n    // Recalculate coordinates',start)
        motion=motion[:start]+'      return cleanupJourney;\n'+motion[end:]
    (out/'app/motion.tsx').write_text(motion,encoding='utf-8')
    landing=(site/'app/landing.tsx').read_text(encoding='utf-8')
    lines=landing.splitlines()
    for i,line in enumerate(lines):
        if '<div className="journey-frame"><Visual' in line:
            alt='PNPLINE logistics journey, rendered in Cycles.' if lang=='en' else 'PNPLINE 物流旅程三维示意图。'
            lines[i]=f' <div className="journey-frame"><img className="journey-fallback" src="/assets/video/hero-b-v002-poster.webp" width={{1920}} height={{1080}} fetchPriority="high" alt="{alt}"/>'
        elif 'poster="/assets/video/hero-poster.jpg"' in line:
            lines[i]=line.replace('hero-poster.jpg','hero-b-v002-poster.webp')
        elif '<img className="journey-final"' in line:
            lines[i]=' <img className="journey-final" src="/assets/video/hero-b-v002-final.webp" alt="" width={1920} height={1080}/>'
        elif '<div className="journey-caption"' in line:
            labels=json.dumps(CAPTIONS[lang],ensure_ascii=False)
            lines[i]=f' <div className="journey-caption" aria-hidden="true">{{{labels}.map((text,i)=><div className="journey-label" key={{text}}><small>CN → US　 /　 0{{i+1}}</small><strong>{{text}}</strong></div>)}}</div></div>'
        elif '<nav className="container route-legend"' in line:
            aria='Logistics video stages' if lang=='en' else '物流视频阶段'
            labels=json.dumps(LABELS[lang],ensure_ascii=False)
            lines[i]=f' <nav className="container route-legend" aria-label="{aria}">{{{labels}.map(text=><button type="button" disabled key={{text}}>{{text}}</button>)}}</nav></div></div></section>'
    (out/'app/landing.tsx').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    css=(site/'app/section-motion.css').read_text(encoding='utf-8')
    css=css.replace('url("/assets/video/hero-poster.jpg")','url("/assets/video/hero-b-v002-poster.webp")')
    if '/* B Cycles publication */' not in css:
        css+='''\n/* B Cycles publication: 7 approved sections, stable viewport, poster-first loading. */
.journey-track[data-video="active"] .journey-screen { height:100svh; }
.journey-track[data-video="active"] .route-legend { grid-template-columns:repeat(7,minmax(0,1fr)); }
@media(max-width:767px) {
  .journey-track[data-video="active"] .route-legend { grid-template-columns:repeat(4,minmax(0,1fr)); row-gap:0; font-size:10px; }
  .journey-track[data-video="active"] .journey-caption { bottom:calc(max(22px,env(safe-area-inset-bottom)) + 110px); }
}
'''
    (out/'app/section-motion.css').write_text(css,encoding='utf-8')
    blinds=(site/'app/section-blinds.tsx').read_text(encoding='utf-8')
    blinds=blinds.replace('Math.max(560, innerHeight * 1.1)', 'Math.max(560, (document.querySelector<HTMLElement>(".journey-screen")?.offsetHeight || innerHeight) * 1.1)')
    (out/'app/section-blinds.tsx').write_text(blinds,encoding='utf-8')
    conf=(site/'next.config.ts').read_text(encoding='utf-8')
    if 'hero-b-v002-:asset' not in conf:
        assert 'poweredByHeader: false' in conf
        conf=conf.replace('poweredByHeader: false','''poweredByHeader: false,
  async headers() { return [{ source: "/assets/video/hero-b-v002-:asset", headers: [
    { key: "Cache-Control", value: "public, max-age=31536000, immutable" }
  ] }]; }''')
    (out/'next.config.ts').write_text(conf,encoding='utf-8')
    shutil.copy2(ROOT/'scripts/hero-journey.ts',out/'app/hero-journey.ts')
    shutil.copy2(REPO/'output/hero-section-b-scroll-v001/mapping.mjs',out/'app/hero-mapping.js')
    config=json.loads((REPO/'output/hero-section-b-scroll-v001/pacing.json').read_text(encoding='utf-8'))
    config.update(version='hero-b-cycles-web-v002',media='/assets/video/hero-b-v002-1080p.mp4',poster='/assets/video/hero-b-v002-poster.webp',previewRenderer='CYCLES_OPTIX')
    (out/'app/hero-pacing.json').write_text(json.dumps(config,ensure_ascii=False,indent=2),encoding='utf-8')
    return out

p=argparse.ArgumentParser();p.add_argument('--apply',action='store_true');a=p.parse_args()
report={}
for lang,site in SITES.items():
    out=stage(lang,site)
    report[lang]={'site':str(site),'stage':str(out)}
    if a.apply:
        required=['hero-b-v002-1080p.mp4','hero-b-v002-720p.mp4','hero-b-v002-poster.webp','hero-b-v002-final.webp','hero-b-v002-manifest.json']
        assert all((ROOT/'assets'/name).exists() for name in required),'Encode assets before application'
        changed=['app/motion.tsx','app/landing.tsx','app/section-motion.css','app/section-blinds.tsx','app/hero-journey.ts','app/hero-mapping.js','app/hero-pacing.json','next.config.ts']
        for rel in changed:
            item=out/rel;dest=site/rel;backup=ROOT/'site-backup'/lang/rel
            backup.parent.mkdir(parents=True,exist_ok=True)
            if dest.exists() and not backup.exists():shutil.copy2(dest,backup)
            dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(item,dest)
        for name in required:shutil.copy2(ROOT/'assets'/name,site/'public/assets/video'/name)
        report[lang]['applied']=True
(ROOT/'audit/site-application.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
