from pathlib import Path
from PIL import Image
import hashlib,json,datetime
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'output/scroll-world-concept-v1';checks=[]
def check(name,ok,detail=None):checks.append({'name':name,'pass':bool(ok),'detail':detail})
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
for p in OUT.rglob('*.json'):
 try:read(p);check('JSON '+str(p.relative_to(OUT)),True)
 except Exception as e:check('JSON '+str(p),False,str(e))
m=read(OUT/'data/assets.json');assets=m['assets'];frames=[a for a in assets if a['kind']=='clean-branded'];styles=[a for a in assets if a['kind']=='styleframe']
check('12 clean branded frames',len(frames)==12);check('3 styleframes',len(styles)==3);check('6 desktop / 6 mobile',all(sum(a['orientation']==o for a in frames)==6 for o in ['desktop','mobile']))
for a in assets:
 p=OUT/a['path'];check('nonempty '+a['asset_id'],p.is_file() and p.stat().st_size>0)
 if p.is_file():
  im=Image.open(p);check('actual size '+a['asset_id'],[im.width,im.height]==[a['width'],a['height']]);check('sha256 '+a['asset_id'],hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256'])
for a in frames+styles:
 check('prompt '+a['asset_id'],(OUT/'prompts'/a['prompt_id']).is_file())
 check('base '+a['asset_id'],(OUT/a['base_path']).is_file())
 if a['kind']=='styleframe':continue
 check('ratio '+a['asset_id'],a['width']*9==a['height']*16 if a['orientation']=='desktop' else a['width']*16==a['height']*9)
 mask=read(OUT/a['mask_path']);check('mask basis '+a['asset_id'],mask['reference_size']==[a['width'],a['height']] and mask['basis']=='review_layout_measured_against_export')
 for r in mask['regions']:
  x,y,w,h=r['rect'];check('mask bounds '+a['asset_id']+'/'+r['id'],0<=x<=1 and 0<=y<=1 and w>0 and h>0 and x+w<=1.00001 and y+h<=1.00001)
 def overlap(a,b):
  x,y,w,h=a;X,Y,W,H=b;return max(x,X)<min(x+w,X+W)-1e-6 and max(y,Y)<min(y+h,Y+H)-1e-6
 for text in [r for r in mask['regions'] if r['role']=='text_allowed']:
  for protected in [r for r in mask['regions'] if r['role']!='text_allowed']:
   check('safe '+a['asset_id']+'/'+text['id']+'/'+protected['id'],not overlap(text['rect'],protected['rect']))
 check('SVG mask '+a['asset_id'],(OUT/a['mask_path'].replace('.json','.svg')).is_file())
places=read(OUT/'data/logo-placements.json')['placements'];check('14 actual composites',len(places)==14)
for p in places:
 check('quad bounds '+p['id'],len(p['logo_quad'])==4 and all(0<=v<=1 for q in p['logo_quad'] for v in q))
 check('actual homography '+p['id'],p['composited'] and len(p['homography_inverse'])==8)
 check('logo original '+p['id'],hashlib.sha256((OUT/p['source_path']).read_bytes()).hexdigest()==p['logo_source_sha256'])
 check('derived '+p['id'],(OUT/p['derived_path']).is_file())
for source in read(OUT/'data/sources.json')['sources']:
 p=ROOT/source['path'];check('source preserved '+source['asset_id'],hashlib.sha256(p.read_bytes()).hexdigest()==source['sha256']);im=Image.open(p);check('source alpha '+source['asset_id'],im.mode=='RGBA')
logo=Image.open(ROOT/'docs/plan/issue-61-brand-miniature/references/PNP-LINE.webp');check('logo transparency',logo.getchannel('A').getextrema()==(0,255))
trim=Image.open(OUT/'branding/derived/PNP-LINE-trimmed.png');check('trim exact original pixels',trim.tobytes()==logo.crop(logo.getchannel('A').getbbox()).tobytes())
t=read(OUT/'data/timeline.json');check('six timeline segments',len(t['segments'])==6)
for i,s in enumerate(t['segments']):check('timeline contiguous '+s['scene_id'],s['progress']==[i/6,(i+1)/6] and s['time_seconds']==[i*5,(i+1)*5] and (i==5 or s['transition']['next_scene']==f'S0{i+2}'))
check('A reuse integrity',(OUT/'styleframes/S01-A.jpg').read_bytes()==(OUT/'keyframes/desktop/S01.jpg').read_bytes())
check('mobile not desktop pixel reuse',all(next(a['sha256'] for a in frames if a['scene_id']==sid and a['orientation']=='desktop')!=next(a['sha256'] for a in frames if a['scene_id']==sid and a['orientation']=='mobile') for sid in [f'S0{i}' for i in range(1,7)]))
report={'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'head':'89f99568d3216814d1b57334bf467a3fdca8ddca','checks':checks,'passed':sum(c['pass'] for c in checks),'failed':[c for c in checks if not c['pass']],'scope':'file/coordinate checks, not visual approval'}
(OUT/'qa/technical-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'checks':len(checks),'passed':report['passed'],'failed':report['failed']},ensure_ascii=False,indent=2));raise SystemExit(bool(report['failed']))
