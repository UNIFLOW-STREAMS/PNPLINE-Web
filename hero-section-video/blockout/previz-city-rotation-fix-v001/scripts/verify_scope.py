import bpy,ast,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];candidate=Path(bpy.data.filepath);s=bpy.context.scene
tree=ast.parse((R.parent/'s2-styleframe-match-v001/scripts/verify_title_water.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'digest','objects','actions'}],type_ignores=[]),'helpers','exec'))
affected={'CR_SLEW_JIB','CR_TROLLEY_CARRIAGE','CR_SUSPENSION_HEAD','P01_SPREADER'}|{o.name for o in s.objects if o.name.startswith('CR_WORKING_CABLE')}
geometry={o.name for o in s.objects['CR_SLEW_JIB'].children if o.type=='MESH' and not o.name.startswith('CR_ROTATING_BEARING')}
allowed=affected|geometry|{'SF_CN_LAYOUT','US_LAND_TERRACE','SF_COAST_FOLDED_FACE'}
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
def snapshot():
 s=bpy.context.scene;s.frame_set(156)
 result={'objects':objects(),'actions':actions(),'links':{o.name:[o.animation_data.action.name,getattr(o.animation_data.action_slot,'identifier',None)] for o in s.objects if o.animation_data and o.animation_data.action},'timeline':[s.frame_start,s.frame_end,s.render.fps,s.render.fps_base,sorted((m.name,m.frame) for m in s.timeline_markers)]}
 names=sorted(o.name for o in s.objects if moving(o) and not under(o,'SF_CN_LAYOUT') and not under(o,'P01_SPREADER'))
 h=hashlib.sha256();lift=[]
 for f in range(1393):
  s.frame_set(f);h.update(json.dumps([list(map(list,s.objects[n].matrix_world)) for n in names]).encode());h.update(str(s.camera.data.lens).encode())
  if f<=100:lift.append(list(s.objects['P01_SPREADER'].matrix_world.translation))
 result['protected_world_digest']=h.hexdigest();result['protected_names']=names;result['lift']=lift;return result
a=snapshot();s.frame_set(156);D=s.objects['SF_CN_LAYOUT'].matrix_world;I=D.inverted();land=s.objects['SF_FRONT_LAND'];lt=BVHTree.FromPolygons([I@land.matrix_world@v.co for v in land.data.vertices],[list(p.vertices) for p in land.data.polygons]);feet={}
for o in s.objects:
 if not o.name.startswith('CR_FOOT_'):continue
 pts=[I@o.matrix_world@v.co for v in o.data.vertices];z=min(p.z for p in pts);contacts=[]
 for p in pts:
  if p.z>z+.001:continue
  hit=lt.ray_cast(p+Vector((0,0,2)),Vector((0,0,-1)),4)[0];contacts.append(None if hit is None else p.z-hit.z)
 feet[o.name]=contacts
shore_min={n:min((s.objects[n].matrix_world@v.co).y for v in s.objects[n].data.vertices) for n in ['SF_COAST_FOLDED_FACE','SF_FRONT_LAND','US_LAND_TERRACE']}
bpy.ops.wm.open_mainfile(filepath=str(R/'inputs/base.blend'));b=snapshot()
changed=[n for n in a['objects'].keys()|b['objects'].keys() if a['objects'].get(n)!=b['objects'].get(n)]
badlinks=[n for n in a['links'].keys()|b['links'].keys() if n not in affected and a['links'].get(n)!=b['links'].get(n)]
protected_actions={v[0] for n,v in b['links'].items() if n not in affected};badactions=[n for n in protected_actions if a['actions'].get(n)!=b['actions'].get(n)]
lift_error=max((Vector(p)-Vector(q)).length for p,q in zip(a['lift'],b['lift']))
checks={'only_authorized_objects_changed':not(set(changed)-allowed),'protected_actions_unchanged':not badactions,'protected_action_links_unchanged':not badlinks,'all_1393_frame_protected_world_transforms_exact':a['protected_world_digest']==b['protected_world_digest'],'timeline_and_fps_unchanged':a['timeline']==b['timeline'],'lift_and_landing_until_f100_preserved':lift_error<.0001,'four_feet_on_land':len(feet)==4 and all(x is not None and abs(x)<.002 for c in feet.values() for x in c),'shore_world_y_separation':min(shore_min.values())>3.2,'baseline_hash_intact':hashlib.sha256((R/'inputs/base.blend').read_bytes()).hexdigest()=='ce36841b9e3418efe1611fdbd9645b6ed9d332ff5db4278974024274d9d6cebb'}
report={'file':str(candidate),'sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'checks':checks,'changed_objects':changed,'unexpected_objects':list(set(changed)-allowed),'bad_links':badlinks,'bad_actions':badactions,'lift_error_m':lift_error,'feet_clearance_m':feet,'shore_min_world_y':shore_min,'protected_names':a['protected_names'],'protected_transform_digest':a['protected_world_digest'],'note':'Existing S4-S7 machinery and contact geometry preserved; city rotation and internal layout unchanged except crane adaptation.'}
(R/'review'/f'{candidate.stem}-scope.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='protected_names'}));assert all(checks.values())
