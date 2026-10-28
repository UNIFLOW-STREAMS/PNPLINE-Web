"""Fresh proposal-only checks, original motion retention and visible obstructions."""
import bpy,sys,json,hashlib,math,importlib.util,unittest,numpy as np
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];candidate=Path(bpy.data.filepath);s=bpy.context.scene
suite=unittest.TestSuite()
for path,cls in [(R/'tests/feature_presence.py','FeatureTests'),(R.parent/'s5-integration-v001/tests/master_regression.py','MasterTests')]:
 spec=importlib.util.spec_from_file_location(cls,path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(getattr(mod,cls)))
res=unittest.TextTestRunner(verbosity=2).run(suite)
result={'candidate':str(candidate),'sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'tests':res.testsRun,'failures':[(str(t),trace)for t,trace in res.failures],'errors':[(str(t),trace)for t,trace in res.errors]}
def action_sig(o):
 ad=o.animation_data
 return hashlib.sha256(json.dumps([[fc.data_path,fc.array_index,[[list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation]for k in fc.keyframe_points]]for l in ad.action.layers for st in l.strips for bag in st.channelbags for fc in bag.fcurves],sort_keys=True).encode()).hexdigest() if ad and ad.action else None
def states():
 sc=bpy.context.scene;data={};names=[o.name for o in sc.objects if o.animation_data and o.name not in ['CAM_MASTER','CAM_LOOK_TARGET']]
 for f in np.arange(0,1392.001,.25):
  sc.frame_set(int(f),subframe=float(f%1))
  mats=[list(map(list,sc.objects[n].matrix_world))for n in names]
  data[float(f)]=hashlib.sha256(np.asarray(mats,dtype=np.float32).tobytes()).hexdigest()
 return names,data,{n:action_sig(sc.objects[n])for n in names}
cnames,cposes,cactions=states();cameras={}
for f in np.arange(0,1392.001,.25):
 s.frame_set(int(f),subframe=float(f%1));cameras[float(f)]=[list(map(list,s.objects[n].matrix_world))for n in ['CAM_MASTER','CAM_LOOK_TARGET']]
occlusion=[];camerabounds=[];s.frame_set(156)
newmeshes=[o for o in s.objects if o.get('styleframe_owner') and o.type=='MESH']
for f in [0,48,72,96,124,144,156,170,180,216,240,278,330,450,456,532,632]:
 s.frame_set(f);origin=s.camera.matrix_world.translation.copy();target=s.objects['A01_CONTAINER'].matrix_world.translation.copy();direction=(target-origin).normalized();dist=(target-origin).length;hits=[]
 for o in newmeshes:
  inv=o.matrix_world.inverted();p=inv@origin;localdir=(inv.to_3x3()@direction).normalized()
  hit,point,_,_=o.ray_cast(p,localdir)
  if hit and (o.matrix_world@point-origin).length<dist-.05:hits.append(o.name)
  if all(min(c[i]for c in o.bound_box)<=p[i]<=max(c[i]for c in o.bound_box)for i in range(3)):camerabounds.append([f,o.name])
 if hits:occlusion.append({'frame':f,'ray':'camera to hero centre, not all visible pixels','objects':hits})
result['new_geometry_center_ray_occlusions']=occlusion;result['camera_inside_new_local_aabb']=camerabounds
bpy.ops.wm.open_mainfile(filepath=str(R/'inputs/base.blend'));names,poses,actions=states()
result['noncamera_action_equal']=actions==cactions;result['noncamera_evaluations_equal']=poses==cposes;result['quarter_frame_samples']=len(poses)
result['outside_s2_camera_differences']=[];result['boundary_delta']={}
for f in np.arange(0,1392.001,.25):
 s=bpy.context.scene;s.frame_set(int(f),subframe=float(f%1));rows=[list(map(list,s.objects[n].matrix_world))for n in ['CAM_MASTER','CAM_LOOK_TARGET']]
 if not 97<f<215 and rows!=cameras[float(f)]:result['outside_s2_camera_differences'].append(float(f))
 if f in [96,97,215,216]:result['boundary_delta'][str(f)]=float(np.max(np.abs(np.asarray(rows)-np.asarray(cameras[float(f)]))))
(R/'review/proposal-qa.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ['failures','errors']},indent=2))
