import bpy,importlib.util,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];B=R.parents[1]/'blockout';OUT=R/'audit'
spec=importlib.util.spec_from_file_location('audit',B/'us-title-curve-v001/scripts/audit_preservation.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
dst=R/'candidate.blend';sha=a.sha(dst)
bpy.ops.wm.open_mainfile(filepath=str(dst));s=bpy.context.scene;s.frame_set(0)
actors={'A04_PRIMARY','A05_SECONDARY'}
ground_prefixes=('DSP_CONTINUOUS_GROUND','DSP_GROUND_EDGE','DSP_ROAD_','DSP_SIDEWALK_','DSP_CURB_','DSP_LANE_','DSP_EDGE_LINE_','DSP_RAIN_GARDEN','DSP_WATERFRONT_PROMENADE','DSP_PROMENADE_JOINT_','DSP_APRON_')
obs=[o for o in s.objects if o.name.startswith('DSP_') and o.type in {'MESH','CURVE','FONT'} and a.visible(o) and not a.under(o,actors) and not o.name.startswith(ground_prefixes)]
body=[o for o in s.objects if o.type in {'MESH','CURVE','FONT'} and a.visible(o) and a.under(o,actors)]
static,names=a.combine(obs);moving=a.GeometryTree(body)
counts={'stationary_obstacle_objects':len(obs),'moving_truck_objects':len(body),'truck_details_in_moving_set':sum(o.name.startswith('DSP_') for o in body)}
obstacle_names=sorted(o.name for o in obs)
body_names=[o.name for o in body];tracked=a.motion_names(s)
a.minimize_scene(s,tracked,body_names)
contacts={};swept_corner_hits={};previous={};samples=[]
for tick in range(1740,1979):
 f=tick/2;s.frame_set(int(f),subframe=f%1);moving.update();samples.append(f)
 if static and moving.tree:
  for ia,ib in static.overlap(moving.tree):contacts.setdefault(names[ia]+' | '+moving.names[ib],set()).add(f)
 for obj,vertices,polygons,corners in moving.geometry:
  current=[obj.matrix_world@p for p in corners]
  if obj.name in previous:
   for idx,(p,q) in enumerate(zip(previous[obj.name],current)):
    d=q-p;ln=d.length
    if ln<1e-8:continue
    hit,nor,ix,dist=static.ray_cast(p,d/ln,ln)
    if hit is not None:swept_corner_hits.setdefault(names[ix]+' | '+obj.name,set()).add(f)
  previous[obj.name]=current
 if tick%40==0:print('TRUCK_CLEARANCE',f,'overlap_pairs',len(contacts),'swept_corner_pairs',len(swept_corner_hits),flush=True)
report={'candidate_sha256':sha,'candidate_immutable':a.sha(dst)==sha,'counts':counts,'sampling':{'first':870,'last':989,'interval':.5,'samples':len(samples)},'passed':not contacts and not swept_corner_hits and a.sha(dst)==sha,
 'triangle_overlap_contacts':{k:sorted(v) for k,v in contacts.items()},'swept_bounding_corner_intersections':{k:sorted(v) for k,v in swept_corner_hits.items()},
 'excluded_expected_ground_contact_prefixes':ground_prefixes,
 'stationary_obstacles':obstacle_names,
 'scope':'Actual evaluated truck body and detail triangles against new stationary architecture, trees, shrubs, furniture, shoreline rocks and warehouse details at every half frame870-989; supplemental rays track every per-mesh bounding-box corner between samples. This is a dense sampled surface check with corner sweeps, not an exhaustive continuous swept-volume proof. Ground, road, sidewalk, curb, paint and apron contact surfaces excluded.'}
(OUT/'truck-clearance.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('TRUCK_CLEARANCE_RESULT',json.dumps(report),flush=True)
assert report['passed'],'See truck-clearance.json'
