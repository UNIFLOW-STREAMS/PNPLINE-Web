import bpy,json,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(0)
label=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'baseline'
step=int(sys.argv[sys.argv.index('--')+2]) if '--' in sys.argv and len(sys.argv)>sys.argv.index('--')+2 else 6
def moving(o):
 while o:
  if o.animation_data and o.animation_data.action:return True
  o=o.parent
 return False
def ancestor(o,n):
 while o:
  if o.name==n:return True
  o=o.parent
 return False
def root(o):
 while o.parent:o=o.parent
 return o.name
visible=[o for o in s.objects if o.type=='MESH'and not o.hide_render]
dynamic=[o for o in visible if moving(o)];static=[o for o in visible if not moving(o)and (ancestor(o,'CN_FRAME')or ancestor(o,'US_FRAME'))]
info={}
for n in ['SF_COAST_FOLDED_FACE','SF_FRONT_LAND','US_LAND_TERRACE','US_QUAY','CN_FRAME','SF_CN_LAYOUT','US_FRAME','CR_COMPACT_GANTRY','CR_SLEW_JIB','A02_SHIP','SF_HULL_BLUE','SF_HULL_RED','P01_SPREADER','A01_CONTAINER']:
 o=s.objects.get(n)
 if not o:continue
 frame=s.objects['SF_CN_LAYOUT'if n.startswith(('SF_COAST','SF_FRONT','CR_'))else 'US_FRAME'if n.startswith('US_')else 'A02_SHIP'].matrix_world.inverted();pts=[frame@o.matrix_world@v.co for v in o.data.vertices]if o.type=='MESH'else [frame@o.matrix_world.translation]
 info[n]={'type':o.type,'parent':o.parent.name if o.parent else None,'min':[min(v[i]for v in pts)for i in range(3)],'max':[max(v[i]for v in pts)for i in range(3)],'location':list(o.location),'matrix':list(map(list,o.matrix_world)),'vertices':[list(v.co)for v in o.data.vertices]if o.type=='MESH'and len(o.data.vertices)<20 else None}
(R/'review'/f'{label}-inspection.json').write_text(json.dumps({'geometry':info,'dynamic_meshes':[{'name':o.name,'parent':o.parent.name if o.parent else None,'root':root(o)}for o in dynamic],'static_count':len(static)},indent=2))
vs=[];fs=[];owners=[]
for o in static:
 k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend(tuple(k+i for i in p.vertices)for p in o.data.polygons);owners.extend([o.name]*len(o.data.polygons))
env=BVHTree.FromPolygons(vs,fs);hits={}
for f in range(0,1393,step):
 s.frame_set(f)
 for o in dynamic:
  vs=[o.matrix_world@v.co for v in o.data.vertices];fs=[tuple(p.vertices)for p in o.data.polygons]
  if not fs:continue
  tree=BVHTree.FromPolygons(vs,fs)
  for name in set(owners[j]for _,j in tree.overlap(env)):
   hits.setdefault(o.name+' | '+name,[]).append(f)
 if f%120==0:print('SCAN',f,len(hits),flush=True)
(R/'review'/f'{label}-coarse-collisions.json').write_text(json.dumps(hits,indent=2));print('DONE',len(hits))
