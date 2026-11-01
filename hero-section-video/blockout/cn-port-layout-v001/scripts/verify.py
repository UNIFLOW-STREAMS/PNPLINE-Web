import bpy,ast,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];candidate=Path(bpy.data.filepath);s=bpy.context.scene
tree_ast=ast.parse((R.parent/'s2-styleframe-match-v001/scripts/verify_title_water.py').read_text());exec(compile(ast.Module(body=[n for n in tree_ast.body if isinstance(n,ast.FunctionDef)and n.name in {'digest','objects','actions'}],type_ignores=[]),'helpers','exec'))
def under(o,n):
 while o:
  if o.name==n:return True
  o=o.parent
 return False
def tree(obs):
 vs=[];fs=[];ns=[]
 for o in obs:
  k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend(tuple(k+i for i in p.vertices)for p in o.data.polygons);ns.extend([o.name]*len(o.data.polygons))
 return BVHTree.FromPolygons(vs,fs),ns
def snap():
 s=bpy.context.scene;s.frame_set(0);a=actions();cam=[];rel=[];later=[];world=[]
 for k in range(625):
  t=k/4;s.frame_set(int(t),subframe=t%1);I=s.objects['A02_SHIP'].matrix_world.inverted();rel.append([list(map(list,I@s.objects[n].matrix_world))for n in ['A01_CONTAINER','P01_SPREADER','W01_NEW_PALLET']]);world.append(list(s.objects['A02_SHIP'].matrix_world.translation))
 for f in range(1393):
  s.frame_set(f);cam.append([list(map(list,s.camera.matrix_world)),s.camera.data.lens])
  if f>=360:later.append([list(map(list,s.objects[n].matrix_world))for n in ['A02_SHIP','A01_CONTAINER','W01_NEW_PALLET']])
 return a,cam,rel,later,world
a,cam,rel,later,world=snap();s.frame_set(0)
envobs=[o for o in s.objects if o.type=='MESH'and not o.hide_render and (under(o,'PORT_MODEL_ROOT')or o.name=='CN_QUAY')];env,en=tree(envobs)
actors=[o for o in s.objects if o.type=='MESH'and not o.hide_render and any(under(o,n)for n in ['A02_SHIP','A01_CONTAINER','P01_SPREADER','CR_SLEW_JIB','CR_TROLLEY_CARRIAGE','CR_SUSPENSION_HEAD'])];hits={}
for k in range(721):
 t=k/2;s.frame_set(int(t),subframe=t%1);at,an=tree(actors)
 for i,j in at.overlap(env):hits.setdefault(an[i]+' | '+en[j],[]).append(t)
 if k%120==0:print('CONTACT',t,len(hits),flush=True)
I=s.objects['SF_CN_LAYOUT'].matrix_world.inverted();s.frame_set(0);feet={o.name:min((I@o.matrix_world@v.co).z for v in o.data.vertices)for o in s.objects if o.name.startswith('CR_FOOT_')}
bpy.ops.wm.open_mainfile(filepath=str(R/'inputs/base.blend'));b,bc,br,bl,bw=snap()
def err(x,y):
 if isinstance(x,(list,tuple)):return max((err(p,q)for p,q in zip(x,y)),default=0)
 return abs(x-y)
checks={'original_actions_exact':all(a.get(n)==h for n,h in b.items()),'all_camera_frames_exact':cam==bc,'S1_relative_ship_cargo_hoist_payload_preserved':err(rel,br)<.0001,'downstream_logistics_f360_plus_exact':err(later,bl)<.0001,'moving_actors_clear_new_port':not hits,'four_crane_feet_on_deck':len(feet)==4 and all(abs(v-1.25)<.0001 for v in feet.values())}
r={'file':str(candidate),'sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'checks':checks,'relative_error':err(rel,br),'later_error':err(later,bl),'feet_z':feet,'crossings':{n:sorted(set(v))for n,v in hits.items()},'sampling':{'relative_step':.25,'contacts_step':.5,'contact_range':[0,360]}}
(R/'review/verification.json').write_text(json.dumps(r,indent=2));print(checks);assert all(checks.values())
