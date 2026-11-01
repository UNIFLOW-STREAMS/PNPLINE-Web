"""Read-only intersections between distinct new architectural sites."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];FILE=ROOT/'pnpline-cn-city-expansion-v001.blend'
sha=hashlib.sha256(FILE.read_bytes()).hexdigest();delivery=json.loads((ROOT/'delivery.json').read_text())
assert delivery['sha256']==sha
bpy.ops.wm.open_mainfile(filepath=str(FILE));s=bpy.context.scene;s.frame_set(0);I=s.objects['SF_CN_LAYOUT'].matrix_world.inverted()
sites=[]
for site in delivery['sites']:
 root=s.objects[site['root']];objects=[o for o in root.children_recursive if o.type=='MESH'and not o.hide_render]
 vs=[];fs=[];names=[]
 for o in objects:
  M=I@o.matrix_world;n=len(vs);vs.extend(M@v.co for v in o.data.vertices);fs.extend(tuple(n+i for i in p.vertices)for p in o.data.polygons);names.extend([o.name]*len(o.data.polygons))
 if not vs:continue
 box=([min(v[i]for v in vs)for i in range(3)],[max(v[i]for v in vs)for i in range(3)])
 sites.append({'name':site['name'],'bounds':box,'tree':BVHTree.FromPolygons(vs,fs),'faces':names})
conflicts=[];landscape_contacts=[];broad=0
for i,a in enumerate(sites):
 for b in sites[i+1:]:
  if not all(a['bounds'][0][j]<=b['bounds'][1][j]and b['bounds'][0][j]<=a['bounds'][1][j]for j in range(3)):continue
  broad+=1;overlap=a['tree'].overlap(b['tree'])
  if overlap:
   row={'a':a['name'],'b':b['name'],'triangle_crossings':len(overlap),'mesh_pairs':sorted(set((a['faces'][x],b['faces'][y])for x,y in overlap))}
   if all((x.endswith('_paving')and 'WALL_HILLS'in y)or(y.endswith('_paving')and 'WALL_HILLS'in x)for x,y in row['mesh_pairs']):landscape_contacts.append(row)
   else:conflicts.append(row)
report={'sha256':sha,'sites':len(sites),'broadphase_pairs':broad,'conflicts':conflicts,
        'landscape_contacts':landscape_contacts,'bounds':{r['name']:r['bounds']for r in sites},'file_unchanged':hashlib.sha256(FILE.read_bytes()).hexdigest()==sha}
(ROOT/'review/site-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'sha256':sha,'sites':len(sites),'broadphase':broad,'conflicts':conflicts},indent=2),flush=True)
