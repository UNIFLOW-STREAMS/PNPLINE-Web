import bpy,sys,json,argparse,itertools
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from geometry import hull,overlap,point_distance
p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--output-dir',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);cfg=json.loads(Path(a.config).read_text());s=bpy.data.scenes[cfg['test_scene']];bpy.context.window.scene=s;P='S5T__'
roots=[bpy.data.objects[P+n] for n in ['A03_TRACTOR','A03_TRAILER','A01_CONTAINER']];moving=set(o for r in roots for o in r.children_recursive if o.type=='MESH');doors=[bpy.data.objects[P+'A01_DOOR_'+n+'_LEAF'] for n in ['LEFT','RIGHT']]
walls=[o for o in s.objects if o.type=='MESH' and any(k in o.name for k in ['WAREHOUSE_','RACK_','DOCK_BRIDGE'])]
body=[bpy.data.objects[P+'A01_'+n] for n in ['FLOOR','ROOF','SIDE_L','SIDE_R','FRONT']]
wheels=[o for o in moving if '_WHEEL_' in o.name];pairs=set()
for o in moving:
 for w in walls:
  if o.name==P+'A01_FLOOR' and w.name==P+'DOCK_BRIDGE':continue
  pairs.add((o,w))
for d in doors:
 for b in body:pairs.add((d,b))
for x,y in itertools.combinations(wheels,2):pairs.add((x,y))
# Tractor cab/chassis against container solids; internal construction joints excluded.
tractor=[o for o in roots[0].children_recursive if o.type=='MESH' and '_WHEEL_' not in o.name]
for x in tractor:
 for y in body+doors:pairs.add((x,y))
errors=[];maximum=0.;camera_clear=float('inf');tests=0;contacts=[]
for i in range(648*4,900*4+1):
 f=i/4;s.frame_set(int(f),subframe=f%1);cache={o:hull(o) for o in moving|set(walls)};bounds={o:([min(v[j] for v in h[0]) for j in range(3)],[max(v[j] for v in h[0]) for j in range(3)]) for o,h in cache.items()}
 for x,y in pairs:
  tests+=1;ax,bx=bounds[x];ay,by=bounds[y]
  if any(bx[j]<=ay[j] or by[j]<=ax[j] for j in range(3)):continue
  d=overlap(*cache[x],*cache[y]);maximum=max(maximum,d)
  if d>cfg['thresholds']['solid_penetration_m']:errors.append(dict(frame=f,pair=[x.name,y.name],depth=d))
 cam=bpy.data.objects[P+'CAM_OBLIQUE'].matrix_world.translation
 for o in moving|set(walls):
  dist=point_distance(o,cam);camera_clear=min(camera_clear,dist)
  if dist<cfg['thresholds']['camera_margin_m']:errors.append(dict(frame=f,camera=o.name,distance=dist))
 if f in [849,890,900]:contacts.append(dict(frame=f,bridge_floor_overlap=overlap(*cache[bpy.data.objects[P+'A01_FLOOR']],*cache[bpy.data.objects[P+'DOCK_BRIDGE']])))
out=dict(pass_all=not errors,errors=errors,pair_checks=tests,maximum_forbidden_overlap=maximum,camera_min_clearance=camera_clear,designated_contacts=contacts,method='Per-mesh convex vertex projections on OBB axes and cross-axes; box exact, wheels conservative. 0.25 frame full interval. Internal chassis/hitch/cargo construction contacts excluded; bridge-floor interface reported. No continuous-time or precise tyre dynamics claim.')
Path(a.output_dir).mkdir(parents=True,exist_ok=True);(Path(a.output_dir)/'space-validation.json').write_text(json.dumps(out,indent=2),encoding='utf8');print('SPACE',out['pass_all'],'errors',len(errors),'maximum',maximum,'camera',camera_clear);print(errors[:8]);assert out['pass_all']
