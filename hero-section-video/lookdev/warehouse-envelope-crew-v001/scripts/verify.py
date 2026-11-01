import bpy,sys,math,json,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1]
B=R.parents[1]/'blockout'
sys.path[:0]=[str(R.parent/'us-warehouse-curvature-v001/scripts'),str(B/'curvature-rework-v001/scripts'),str(R.parent/'container-ship-v001/scripts')]
from surface_site import sphere,arc,basis
S=bpy.context.scene
U=S.objects['US_FRAME']
def flat(p):return arc(np.array(U.matrix_world.inverted()@Vector(p)))
def loc(o):return flat(o.matrix_world.translation).round(3).tolist()
sys.path.insert(0,str(B/'us-title-curve-v001/scripts'))
from audit_preservation import motion_names,minimize_scene,optics,action_signature
from mathutils.bvhtree import BVHTree
report=json.loads((R/'review/build.json').read_text())
s=S
assert s.camera.name=='CAM_MASTER' and s.frame_start==0 and s.frame_end==989 and s.render.fps==30
assert len([o for o in s.objects if o.name.startswith('Figure ') and 'Work shirt, vest and face' in o.name])==3
assert not any(n in s.objects for n in report['removed'])
assert all(s.objects[n].type=='MESH' and len(s.objects[n].data.vertices)==0 for n in ['CH_LOAD_ARM_0','CH_LOAD_ARM_1'])
# Check the physical shell including pre-existing surfaces. Cast normal rays from under the roof,
# through both end elevations, along the front curtain wall and through both unsealed dock mouths.
sv=[o for o in s.objects if o.name.startswith('WHE | ') and o.type=='MESH' or o.name in ('WH_FACADE_HEADER','WH_END_HEADER_36','WH_END_HEADER_68','WH_SIDE_REAR_36','WH_SIDE_REAR_68','WH_SIDE_FRONT_68','WH_FRONT_PIER_68','WH_REAR_WALL','WH_PARTIAL_ROOF','WH_DOCK_LINTEL_36','WH_DOCK_LINTEL_68','WH_INBOUND_REAR_PIER')]
vs=[];fs=[]
for o in sv:
 off=len(vs);mat=U.matrix_world.inverted()@o.matrix_world
 vs.extend([mat@v.co for v in o.data.vertices]);fs.extend([tuple(off+i for i in p.vertices) for p in o.data.polygons])
tree=BVHTree.FromPolygons(vs,fs,all_triangles=False)
def ray(a,b):
 a=Vector(sphere(np.array(a)));b=Vector(sphere(np.array(b)));vec=b-a;return tree.ray_cast(a,vec.normalized(),vec.length)[0] is not None
for_zone={}
def test(name,pairs,value=True):
 failed=[];count=0
 for a,b in pairs:
  count+=1
  if ray(a,b)!=value:failed.append(a)
 for_zone[name]=dict(probes=count,unexpected=len(failed),sample_failures=failed[:5])
test('roof',[((x,y,10.9),(x,y,12.3)) for x in np.linspace(35.85,68.15,70) for y in np.linspace(25.18,39.1,33)])
test('long frontage',[((x,24.65,z),(x,25.6,z)) for x in np.linspace(36.0,68,64) for z in np.linspace(2.0,11.46,23)])
for x in (36,68):
 test('end '+str(x),[((x-.42,y,z),(x+.42,y,z)) for y in np.linspace(25.44,38.96,50) for z in np.linspace(1.96,11.49,42) if not (26.70<y<31.51 and z<5.7)])
 test('dock clear '+str(x),[((x-.42,y,z),(x+.42,y,z)) for y in np.linspace(27.08,30.90,11) for z in np.linspace(2.06,5.45,11)],False)
print('ENVELOPE',for_zone,flush=True)
def snap(s,names,extra):
 s.frame_set(0)
 act={a.name:action_signature(a) for a in bpy.data.actions if not a.name.startswith('Crew pose | ')}
 markers=sorted([(m.name,m.frame) for m in s.timeline_markers])
 minimize_scene(s,names,extra)
 obs=[s.objects[n] for n in names];world=[];lens=[];handerr=[]
 for f in range(990):
  s.frame_set(f);world.append([np.array(o.matrix_world) for o in obs]);lens.append(optics(s.camera))
  if extra:
   for n,i in [('L',1),('R',0)]:
    hand=s.objects['Figure Load | '+n+' grip glove']
    anchor=s.objects['CH_LOADER'].matrix_world;arm=s.objects['CH_LOAD_ARM_'+str(i)]
    target=(arm.matrix_world@Vector((0,0,.5)))+(anchor.to_3x3()@Vector((0,0,.067)))
    handerr.append((target-hand.matrix_world.translation).length)
 return act,markers,lens,np.array(world),max(handerr) if handerr else None
names=[n for n in motion_names(s) if not n.startswith('Figure ')]
c=snap(s,names,['Figure Load | L grip glove','Figure Load | R grip glove','CH_LOADER'])
bpy.ops.wm.open_mainfile(filepath=str(report['archived_source']))
s=bpy.context.scene
assert names==list(motion_names(s));old=snap(s,names,[])
delta=float(np.abs(old[3]-c[3]).max())
v=dict(checked_sha256=__import__('hashlib').sha256(Path(report['output']).read_bytes()).hexdigest(),original_actions=len(old[0]),original_tracked_camera_and_actors=len(names),frames=990,frame_range=[0,989],fps=30,all_original_actions_match=c[0]==old[0],camera_optics_equal=c[2]==old[2],markers_equal=c[1]==old[1],max_world_matrix_difference=delta,maximum_glove_endpoint_error=c[4],envelope=for_zone)
(R/'review/verification.json').write_text(json.dumps(v,indent=2))
print('VERIFICATION',json.dumps(v),flush=True)
assert c[0]==old[0] and c[1]==old[1] and c[2]==old[2] and delta==0 and c[4]<.002
assert not any(v['unexpected'] for v in for_zone.values())


