"""Additional actual-mesh contacts: podium skirt edges, hills, covered wave curves."""
import bpy,json,hashlib
from pathlib import Path
from collections import Counter
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];FILE=ROOT/'pnpline-cn-city-expansion-v001.blend'
sha=hashlib.sha256(FILE.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(FILE));s=bpy.context.scene;s.frame_set(0)
I=s.objects['SF_CN_LAYOUT'].matrix_world.inverted();o=s.objects['CNX_CURVED_DISTRICT_LAND'];M=I@o.matrix_world
tree=BVHTree.FromPolygons([M@v.co for v in o.data.vertices],[tuple(p.vertices)for p in o.data.polygons])
def gap(p):
 hit=tree.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)))[0]
 return p.z-hit.z if hit is not None else None
foundations=[]
for o in s.objects:
 if not o.name.startswith('CNX_')or not(o.name.endswith('_FOUNDATION')or o.name.endswith('_TERRACE'))or o.type!='MESH'or len(o.data.vertices)<8 or len(o.data.vertices)%2:continue
 M=I@o.matrix_world;v=[M@p.co for p in o.data.vertices];half=len(v)//2;samples=[]
 for a,b in zip(v[half:],v[half+1:]+v[half:half+1]):
  for i in range(11):
   p=a.lerp(b,i/10);g=gap(p);samples.append({'point':list(p),'gap':g})
 values=[r['gap']for r in samples if r['gap']is not None]
 foundations.append({'name':o.name,'max_edge_gap':max(values,default=None),'min_edge_gap':min(values,default=None),
                     'missing':sum(r['gap']is None for r in samples),'worst':max((r for r in samples if r['gap']is not None),key=lambda r:r['gap'],default=None)})
waves=[]
for o in s.objects:
 if not o.name.startswith('SF_OCEAN_WAVE')or o.hide_render:continue
 M=I@o.matrix_world;ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();vals=[]
 for v in me.vertices:
  p=M@v.co;g=gap(p)
  if g is not None:vals.append((g,list(p)))
 ev.to_mesh_clear()
 if vals:waves.append({'name':o.name,'samples':len(vals),'exposed':sum(v>.04 for v,p in vals),'max_gap':max(vals)[0],'worst_point':max(vals)[1]})
hills=[]
for o in s.objects:
 if not o.name.startswith('CNX_BJ_WALL_HILLS')or o.type!='MESH':continue
 M=I@o.matrix_world;ec=Counter(tuple(sorted((a,b)))for p in o.data.polygons for a,b in zip(list(p.vertices),list(p.vertices)[1:]+list(p.vertices)[:1]))
 ids=set(i for e,c in ec.items()if c==1 and (o.data.vertices[e[0]].co-o.data.vertices[e[1]].co).length>1e-6 for i in e);points=[]
 for i in ids:
  p=M@o.data.vertices[i].co;g=gap(p);points.append({'point':list(p),'gap':g})
 vals=[r['gap']for r in points if r['gap']is not None]
 hills.append({'name':o.name,'boundary_vertices':len(points),'max_gap':max(vals,default=None),'min_gap':min(vals,default=None),'missing':sum(r['gap']is None for r in points),'points':points})
report={'sha256':sha,'foundations':foundations,'foundation_edge_gaps_above_0_08':[r for r in foundations if r['missing']or r['max_edge_gap']>.08],
        'waves':waves,'wave_protrusions':[r for r in waves if r['exposed']],'hills':hills,
        'file_unchanged':hashlib.sha256(FILE.read_bytes()).hexdigest()==sha}
(ROOT/'review/contact-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'foundation_errors':report['foundation_edge_gaps_above_0_08'],'wave_protrusions':report['wave_protrusions'],'hills':[{k:v for k,v in r.items()if k!='points'}for r in hills]},indent=2),flush=True)
