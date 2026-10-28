"""All-frame crossings of separately moving port assemblies; emit raw contacts.
Do not confuse surface tangency / cargo seating / bearing connections with penetration.
"""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];s=bpy.context.scene
label=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'assemblies'
def under(o,n):
 while o:
  if o.name==n:return True
  o=o.parent
 return False
def group(o):
 if under(o,'A02_SHIP'):return 'ship'
 if under(o,'A01_CONTAINER'):return 'cargo'
 if under(o,'P01_SPREADER') or o.name.startswith('CR_'):return 'cn_crane'
 if o.name.startswith('P02_'):return 'us_crane'
 if under(o,'A03_TRACTOR') or under(o,'A03_TRAILER'):return 'receiver'
 return None
groups={}
for o in s.objects:
 if o.type=='MESH' and not o.hide_render and (g:=group(o)):groups.setdefault(g,[]).append(o)
def tree(obs):
 vs=[];fs=[];names=[]
 for o in obs:
  k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([tuple(k+i for i in p.vertices) for p in o.data.polygons]);names.extend([o.name]*len(o.data.polygons))
 return BVHTree.FromPolygons(vs,fs),names
pairs=[('ship','cargo'),('ship','cn_crane'),('cargo','cn_crane'),('ship','us_crane'),('cargo','us_crane'),('cargo','receiver'),('ship','receiver'),('receiver','us_crane')];hits={}
for f in range(1393):
 s.frame_set(f);data={g:tree(obs) for g,obs in groups.items()}
 for a,b in pairs:
  # Stationary Chinese crane is distant from every actor after the voyage.
  if 'cn_crane' in (a,b) and f>340:continue
  ta,na=data[a];tb,nb=data[b]
  for x,y in set((na[i],nb[j]) for i,j in ta.overlap(tb)):hits.setdefault(x+' | '+y,[]).append(f)
 if f%240==0:print('ASSEMBLIES',f,len(hits),flush=True)
(R/'review'/f'{label}.json').write_text(json.dumps({'file':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'frames':1393,'pairs':pairs,'hits':hits},indent=2));print('DONE',len(hits))
