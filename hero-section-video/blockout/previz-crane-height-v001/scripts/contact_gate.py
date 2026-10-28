"""Regression: actual triangle crossings against shore and fixed crane portal.
Mechanically intended rail/bearing contacts are deliberately not obstruction pairs.
"""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];s=bpy.context.scene
label=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'gate'
def tree(o):
 return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])
def under(o,n):
 while o:
  if o.name==n:return True
  o=o.parent
 return False
env=[s.objects[n] for n in ['SF_COAST_FOLDED_FACE','SF_FRONT_LAND','US_LAND_TERRACE','US_QUAY','CN_QUAY']]
actors=[o for o in s.objects if o.type=='MESH' and not o.hide_render and (under(o,'A02_SHIP') or under(o,'A01_CONTAINER'))]
fixed=[o for o in s.objects if o.type=='MESH' and o.name.startswith(('CR_LEG_','CR_FIXED_PORTAL_CAP','CR_FIXED_SLEW_SEAT'))]
cab=[s.objects[n] for n in ['CR_CAB','CR_CAB_GLASS']]
s.frame_set(0);et=[(o.name,tree(o)) for o in env];ft=[(o.name,tree(o)) for o in fixed];hits={}
for f in range(1393):
 s.frame_set(f)
 # Ship only approaches the ports through f510; landed cargo remains aboard until S4.
 for o in actors:
  if f>672:continue
  t=tree(o)
  for n,e in et:
   if t.overlap(e):hits.setdefault(o.name+' | '+n,[]).append(f)
 for o in cab:
  t=tree(o)
  for n,e in ft:
   if t.overlap(e):hits.setdefault(o.name+' | '+n,[]).append(f)
 if f%240==0:print('GATE',f,len(hits),flush=True)
result={'file':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'frames':1393,'ship_cargo_scan':[0,672],'cab_scan':[0,1392],'crossings':hits,'pass':not hits}
(R/'review'/f'{label}.json').write_text(json.dumps(result,indent=2));print('CONTACT_GATE',result['pass'],len(hits),flush=True)
if hits:raise RuntimeError('Contact regression failed')
