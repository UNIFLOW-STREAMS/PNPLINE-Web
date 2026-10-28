"""Meaningful full-film regression. Run bounded proposal first: range/tail fail."""
import bpy,json,math,sys,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];B=R.parents[1]/'blockout/full-layout-master-v001';(B/'review').mkdir(parents=True,exist_ok=True)
s=bpy.context.scene;checks=[]
def check(name,ok,detail):checks.append({'name':name,'pass':bool(ok),'detail':detail});print(name,ok,detail,flush=True)
check('Full timeline 0-1392, no preview truncation',(s.frame_start,s.frame_end)==(0,1392) and not s.use_preview_range,[s.frame_start,s.frame_end,s.use_preview_range])
for n,f in [('A04_PRIMARY',1201),('A05_SECONDARY',1261)]:
 s.frame_set(f-1);before=s.objects[n].matrix_world.translation.copy();s.frame_set(1392);distance=(s.objects[n].matrix_world.translation-before).length;check(n+' S7 departure restored',distance>10,distance)
s.frame_set(948);p=s.objects['W01_NEW_PALLET'].matrix_world.translation.copy();s.frame_set(970);dist=(s.objects['W01_NEW_PALLET'].matrix_world.translation-p).length;check('S6 pallet continues after948',dist>.05,dist)
last=None;maxstep=0;maxangle=0;worst=[];keels=[];decks=[];clearance=1e9
for j in range(1392*4+1):
 f=j/4;s.frame_set(int(f),subframe=f%1);m=s.camera.matrix_world.copy();q=m.to_quaternion()
 if last:
  step=(m.translation-last.translation).length/.25;angle=2*math.acos(min(1,abs(q.dot(last.to_quaternion()))))/.25
  if step>maxstep:maxstep=step;worst=[f,'position']
  maxangle=max(maxangle,angle)
 last=m;ship=s.objects['A02_SHIP'].matrix_world;clearance=min(clearance,m.translation.length-s['radius'])
 for x in [-6.8,0,6.8]:keels.append((ship@Vector((x,0,-.65))).length-s['radius']);decks.append((ship@Vector((x,0,.8))).length-s['radius'])
check('Camera no jumps throughout film',maxstep<2.5 and maxangle<math.radians(8),{'max_m_frame':maxstep,'max_deg_frame':math.degrees(maxangle),'worst':worst})
check('Ship bow/stern contact ocean at new latitude',max(keels)<-.15 and min(decks)>.6,{'keel_max':max(keels),'deck_min':min(decks)})
check('Camera outside ocean',clearance>.1,clearance)
out=Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else B/'review/full-acceptance.json';out.write_text(json.dumps({'file':bpy.data.filepath,'master_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'checks':checks,'pass':all(x['pass'] for x in checks)},indent=2),encoding='utf8')
if not all(x['pass'] for x in checks):raise AssertionError('Full master checks failed')
