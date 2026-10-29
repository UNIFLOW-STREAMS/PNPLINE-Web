"""Evaluated local-space vehicle clearance against new structure; conservative component bounds."""
import bpy,sys,json,hashlib,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];S=bpy.context.scene;file=Path(bpy.data.filepath);I=S.objects['US_FRAME'].matrix_world.inverted()
def ancestor(o):
 while o.parent:o=o.parent
 return o.name
vehicles=[o for o in S.objects if o.type=='MESH' and ancestor(o) in ['A01_CONTAINER','A03_TRAILER','A03_TRACTOR','A04_PRIMARY','A05_SECONDARY']]
def bounds(o,dep):
 e=o.evaluated_get(dep);m=I@e.matrix_world;v=[m@Vector(c) for c in e.bound_box]
 return [min(p[k] for p in v) for k in range(3)],[max(p[k] for p in v) for k in range(3)]
S.frame_set(1);deps=bpy.context.evaluated_depsgraph_get()
solid=[o for o in S.objects if o.type=='MESH' and (o.get('wh_role') in ['structure','rack','conveyor','equipment'] or o.name=='WAREHOUSE_FLOOR') and not o.animation_data and not any(p.animation_data for p in [o.parent] if p)]
fixed=[(o.name,*bounds(o,deps)) for o in solid];hits=[];seen=set();minimum=1000
frames=sorted(set(range(1,1393))|{f+.5 for f in range(780,1250)}|{f/8 for f in range(744*8,781*8)}|{f/8 for f in range(1248*8,1392*8+1)})
for f in frames:
 S.frame_set(int(f),subframe=f%1);deps=bpy.context.evaluated_depsgraph_get()
 for o in vehicles:
  lo,hi=bounds(o,deps)
  if hi[0]<35 or lo[0]>69 or hi[1]<24 or lo[1]>40:continue
  for name,a,b in fixed:
   overlap=[min(hi[k],b[k])-max(lo[k],a[k]) for k in range(3)]
   if min(overlap)>.005:
    pair=(o.name,name)
    if pair not in seen:hits.append({'frame':f,'moving':o.name,'solid':name,'overlap':overlap});seen.add(pair)
report={'candidate_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'frames':len(frames),'vehicle_components':len(vehicles),'stationary_components':len(fixed),'hits':hits,'method':'Conservative component AABB in US_FRAME. Positive candidates require geometry investigation; no broad root envelope used. Floor contact <= .005 allowed.'}
(R/'review'/f'{file.stem}-clearance.json').write_text(json.dumps(report,indent=2));print('CLEARANCE',len(frames),'frames',len(hits),'pairs');print(json.dumps(hits[:15],indent=2))
if hits:raise AssertionError('Vehicle structure intersections')
