import bpy,json,hashlib
from pathlib import Path
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];s=bpy.context.scene
def under(o,n):
 while o:
  if o.name==n:return True
  o=o.parent
 return False
def moving(o):
 while o:
  if o.animation_data and o.animation_data.action:return True
  o=o.parent
 return False
def tree(obs):
 vs=[];fs=[];names=[]
 for o in obs:
  k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([tuple(k+i for i in p.vertices) for p in o.data.polygons]);names.extend([o.name]*len(o.data.polygons))
 return BVHTree.FromPolygons(vs,fs),names
mesh=[o for o in s.objects if o.type=='MESH' and not o.hide_render];s.frame_set(0)
static=tree([o for o in mesh if under(o,'CN_FRAME') and not moving(o)])
crane=[o for o in mesh if (o.name.startswith('CR_') or under(o,'P01_SPREADER')) and moving(o)]
ship=[o for o in mesh if under(o,'A02_SHIP')];cargo=[o for o in mesh if under(o,'A01_CONTAINER')];hits={};allowed={}
for k in range(1041):
 t=k/4;s.frame_set(int(t),subframe=t%1);c,nc=tree(crane)
 for typ,(e,ne) in [('static',static),('ship',tree(ship)),('cargo',tree(cargo))]:
  for a,b in set((nc[i],ne[j]) for i,j in c.overlap(e)):
   intentional=(a=='CR_ROTATING_BEARING' and b=='CR_FIXED_SLEW_SEAT') or (a.startswith('CR_TWISTLOCK') and b=='A01_ROOF' and t<=82)
   (allowed if intentional else hits).setdefault(a+' | '+b,[]).append(t)
 if k%240==0:print('DENSE',t,len(hits),flush=True)
report={'file':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'sample_range':[0,260],'step':.25,'samples':1041,'unexpected':hits,'intentional_contacts':{n:[min(v),max(v)] for n,v in allowed.items()},'pass':not hits}
(R/'review'/f'{Path(bpy.data.filepath).stem}-dense.json').write_text(json.dumps(report,indent=2));print('DENSE_RESULT',report['pass']);assert not hits
