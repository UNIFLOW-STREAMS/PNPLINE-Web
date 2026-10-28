"""Independent saved-file checks at source-matched integer and contact subframes."""
import bpy,sys,json,hashlib,math,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));sys.path.insert(0,str(R.parent/'s5-dock-test-v001/scripts'))
from motion import TimeMap
from geometry import hull,overlap,point_distance
cfg=json.loads((R/'config.json').read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def frame(s,f):s.frame_set(int(f),subframe=f%1)
def geo(s):return {o.name:hashlib.sha256(np.asarray([v.co[:] for v in o.data.vertices],dtype=np.float64).tobytes()+str([list(p.vertices) for p in o.data.polygons]).encode()).hexdigest() for o in s.objects if o.type=='MESH'}
def qangle(a,b):
 q=a.to_quaternion().rotation_difference(b.to_quaternion());return math.degrees(2*math.atan2(math.sqrt(q.x*q.x+q.y*q.y+q.z*q.z),abs(q.w)))
for variant in sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['A','B']:
 m=TimeMap(1392,cfg['easing'],cfg['compression_B'] if variant=='B' else [])
 times=set(np.arange(0,1392.0001,.25).tolist())
 times.update(m.inverse(f) for f in range(round(m.output_end)+1))
 times.update(np.arange(648,900.0001,.0625).tolist())
 # Independently located source failures at terrain edges; do not lose them
 # merely because the nominal sample grid happens to miss a height discontinuity.
 times.update([700.5450141107419,704.0991761629364,707.2786643890552,709.48074155479,737.0149324809711])
 for e in list(cfg['events'].values())+[96,216,456,648,900,1200]:times.update(max(0,min(1392,e+j/16)) for j in range(-32,33))
 times=sorted(times)
 bpy.ops.wm.open_mainfile(filepath=str(R/'inputs/source.blend'));s=bpy.context.scene;names=sorted(o.name for o in s.objects);geometry=geo(s)
 expected=np.empty((len(times),len(names),4,4),dtype=np.float32);lenses=[]
 for i,f in enumerate(times):
  frame(s,f);expected[i]=np.asarray([s.objects[n].matrix_world[:] for n in names]);lenses.append(s.camera.data.lens)
 print('SOURCE_SAMPLES',variant,len(times),flush=True)
 path=R/f'master-motion-polish-{variant}.blend';bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene
 errors=[];metric={'max_actor_matrix_delta':0.,'max_storyboard_matrix_delta':0.,'max_storyboard_lens_delta':0.,'max_wheel_ground_error_m':0.,'max_hitch_error_m':0.,'max_door_body_penetration_m':0.,'max_cargo_hand_support_error_m':0.,'max_container_support_translation_error_m':0.,'max_camera_patch_displacement_m':0.,'camera_min_clearance_m':10000.}
 assert sorted(set(o.name for o in s.objects)-set(names))==['MP_CONTINUOUS_ROAD'] and all(geo(s)[n]==v for n,v in geometry.items()),'Unauthorized asset geometry or identity changed'
 assert s.render.fps==24 and s.render.fps_base==1 and s.frame_end==round(m.output_end)
 actor_ids=[i for i,n in enumerate(names) if n not in ['CAM_MASTER','CAM_LOOK_TARGET'] and not (n.startswith('A03') and '_WHEEL_' in n)]
 camid=names.index('CAM_MASTER');aimid=names.index('CAM_LOOK_TARGET')
 I=s.objects['US_FRAME'].matrix_world.inverted();wheels=[o for o in s.objects if o.name.startswith('A03') and '_WHEEL_' in o.name]
 road=s.objects['MP_CONTINUOUS_ROAD'];roadverts=[I@road.matrix_world@v.co for v in road.data.vertices]
 assert min(p.x for p in roadverts)>=17-.0001 and max(p.y for p in roadverts)<=26+.0001,'Coplanar road overlap with quay/yard'
 correction_counts=[]
 for wheel in wheels:
  ad=wheel.animation_data;fc=[f for l in ad.action.layers for st in l.strips for b in st.channelbags if b.slot_handle==ad.action_slot.handle for f in b.fcurves if f.data_path=='location']
  kt=[[float(k.co.x) for k in f.keyframe_points if m.forward(648)<=k.co.x<=m.forward(900)] for f in sorted(fc,key=lambda f:f.array_index)]
  assert len(kt)==3 and kt[0]==kt[1]==kt[2] and max(np.diff(kt[0]))<=1/128+.00001,'Dense shared correction breakpoints lost after save'
  correction_counts.append([wheel.name,len(kt[0])])
 ground=[]
 metric.update(legacy_center_ray_error_m=0.,max_tyre_penetration_m=0.,max_tyre_support_gap_m=0.,max_wheel_xy_drift_m=0.)
 for n in ['US_QUAY','US_LAND_TERRACE','E09_MANEUVER_YARD','MP_CONTINUOUS_ROAD']:
  o=s.objects[n];ground.append(BVHTree.FromPolygons([I@o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]))
 doors=[s.objects['A01_DOOR_'+n+'_LEAF'] for n in ['LEFT','RIGHT']];body=[s.objects['A01_'+n] for n in ['FLOOR','ROOF','SIDE_L','SIDE_R','FRONT']]
 relation={};camera_rows=[];event_rows=[];ship_keel_max=-10000.;ship_deck_min=10000.
 for idx,f in enumerate(times):
  otime=m.forward(f);frame(s,otime);actual=np.asarray([s.objects[n].matrix_world[:] for n in names])
  delta=float(np.max(np.abs(actual[actor_ids]-expected[idx,actor_ids])))
  metric['max_actor_matrix_delta']=max(metric['max_actor_matrix_delta'],delta)
  if delta>.002 and len(errors)<20:errors.append(['actor mismatch',f,delta])
  metric['max_camera_patch_displacement_m']=max(metric['max_camera_patch_displacement_m'],float(np.linalg.norm(actual[camid,:3,3]-expected[idx,camid,:3,3])))
  if f in cfg['storyboard_source_frames']:
   story_ids=actor_ids+[camid,aimid];d=float(np.max(np.abs(actual[story_ids]-expected[idx,story_ids])));ld=abs(s.camera.data.lens-lenses[idx]);metric['max_storyboard_matrix_delta']=max(metric['max_storyboard_matrix_delta'],d);metric['max_storyboard_lens_delta']=max(metric['max_storyboard_lens_delta'],ld)
   if d>.0002 or ld>.0001:errors.append(['storyboard pose changed',f,d,ld])
  for wheel in wheels:
   expected_wheel=expected[idx,names.index(wheel.name)];rotation_error=float(np.max(np.abs(actual[names.index(wheel.name),:3,:3]-expected_wheel[:3,:3])))
   delta_world=Vector(actual[names.index(wheel.name),:3,3]-expected_wheel[:3,3]);local_delta=I.to_3x3()@delta_world
   metric['max_wheel_xy_drift_m']=max(metric['max_wheel_xy_drift_m'],math.hypot(local_delta.x,local_delta.y))
   if (rotation_error>.0002 or math.hypot(local_delta.x,local_delta.y)>.0002) and len(errors)<20:errors.append(['wheel lateral/rotation drift',f,wheel.name,rotation_error,list(local_delta)])
   wm=I@wheel.matrix_world;center=wm.translation;hits=[tree.ray_cast(center+Vector((0,0,5)),Vector((0,0,-1)),20)[0] for tree in ground];z=max(p.z for p in hits if p is not None);bottom=min((wm@v.co).z for v in wheel.data.vertices)
   metric['legacy_center_ray_error_m']=max(metric['legacy_center_ray_error_m'],abs(bottom-z))
   # Center-ray equality is invalid on slopes. Keep that historical measure,
   # but enforce the SAME 2mm tolerance on actual tyre/visible-road clearance.
   gap=1000.
   for v in wheel.data.vertices:
    p=wm@v.co
    if p.z>center.z:continue
    hits=[tree.ray_cast(p+Vector((0,0,5)),Vector((0,0,-1)),20)[0] for tree in ground]
    gap=min(gap,p.z-max(h.z for h in hits if h is not None))
   metric['max_wheel_ground_error_m']=max(metric['max_wheel_ground_error_m'],abs(gap))
   metric['max_tyre_penetration_m']=max(metric['max_tyre_penetration_m'],-gap)
   metric['max_tyre_support_gap_m']=max(metric['max_tyre_support_gap_m'],gap)
  if f>=648:metric['max_hitch_error_m']=max(metric['max_hitch_error_m'],(s.objects['TRACTOR_HITCH'].matrix_world.translation-s.objects['TRAILER_HITCH'].matrix_world.translation).length)
  if 85<=f<=510 or f>=637:
   support='A02_SHIP' if f<=510 else 'A03_TRAILER';rel=s.objects[support].matrix_world.inverted()@s.objects['A01_CONTAINER'].matrix_world
   if support not in relation:relation[support]=rel.copy()
   metric['max_container_support_translation_error_m']=max(metric['max_container_support_translation_error_m'],(rel.translation-relation[support].translation).length)
  ship=s.objects['A02_SHIP'].matrix_world
  for x in [-6.8,0,6.8]:
   ship_keel_max=max(ship_keel_max,(ship@Vector((x,0,-.65))).length-s['radius']);ship_deck_min=min(ship_deck_min,(ship@Vector((x,0,.8))).length-s['radius'])
  if 810<=f<=891:
   for door in doors:
    for wall in body:metric['max_door_body_penetration_m']=max(metric['max_door_body_penetration_m'],overlap(*hull(door),*hull(wall)))
  if 1151<=f<=1166:
   box=s.objects['LAST_BOX_BODY'];hand=s.objects['CH_LOAD_SUPPORT'];bottom=min((I@box.matrix_world@Vector(c)).z for c in box.bound_box);top=max((I@hand.matrix_world@Vector(c)).z for c in hand.bound_box)
   metric['max_cargo_hand_support_error_m']=max(metric['max_cargo_hand_support_error_m'],abs(bottom-top))
  if f in cfg['events'].values():event_rows.append({'source_frame':f,'output_frame':otime,'doors':[s.objects['A01_DOOR_'+n].rotation_euler.z for n in ['L','R']]})
  if abs(otime-round(otime))<1e-5:
   camera_rows.append([otime,s.camera.matrix_world.copy(),float(s.camera.data.lens)])
  if idx%2000==0:print('CHECK',variant,idx,'/',len(times),flush=True)
 metric.update(ship_keel_max_above_radius_m=ship_keel_max,ship_deck_min_above_radius_m=ship_deck_min,saved_contact_key_counts=correction_counts)
 for key,limit in [('max_wheel_ground_error_m',.002),('max_hitch_error_m',.002),('max_door_body_penetration_m',.01),('max_cargo_hand_support_error_m',.035),('max_container_support_translation_error_m',.002)]:
  if metric[key]>limit:errors.append([key,metric[key],limit])
 if ship_keel_max>=-.15 or ship_deck_min<=.6:errors.append(['ship water',ship_keel_max,ship_deck_min])
 joins=[]
 for src in sorted(set([96,216,456,648,900,1200]+[x for patch in cfg['camera_patches'] for x in patch])):
  out=m.forward(src);ms=[];ls=[]
  for f in [out-.125,out,out+.125]:frame(s,f);ms.append(s.camera.matrix_world.copy());ls.append(float(s.camera.data.lens))
  speeds=[(b.translation-a.translation).length/.125 for a,b in zip(ms,ms[1:])];jump=((ms[2].translation-ms[1].translation)-(ms[1].translation-ms[0].translation)).length/.125
  rotations=[qangle(a,b)/.125 for a,b in zip(ms,ms[1:])];joins.append({'source':src,'output':out,'speeds':speeds,'velocity_delta':jump,'rotation_deg_per_frame':rotations,'lens_rates':[(b-a)/.125 for a,b in zip(ls,ls[1:])]})
  if min(speeds)<.001 or jump>.15:errors.append(['camera boundary',src,speeds,jump])
 # Check camera path against actual visible solids at every output integer.
 obstacles=[o for o in s.objects if o.type=='MESH' and not o.hide_render and not any(c.name=='08_REVIEW_GUIDES' for c in o.users_collection)]
 camera_path=[]
 for f in range(s.frame_end+1):
  frame(s,f);cam=s.camera.matrix_world.copy();camera_path.append(cam)
  for ob in obstacles:
   # Sphere/globe proxies surround the scene; their AABB is not a solid surface distance.
   if 'GLOBE' in ob.name or 'OCEAN' in ob.name or 'EARTH' in ob.name:continue
   lo=[min((ob.matrix_world@Vector(c))[j] for c in ob.bound_box) for j in range(3)];hi=[max((ob.matrix_world@Vector(c))[j] for c in ob.bound_box) for j in range(3)];p=cam.translation
   if any(p[j]<lo[j]-.12 or p[j]>hi[j]+.12 for j in range(3)):continue
   d=point_distance(ob,p);metric['camera_min_clearance_m']=min(metric['camera_min_clearance_m'],d)
   if d<.12 and len(errors)<25:errors.append(['camera intersects box bound',f,ob.name,d])
 steps=[(b.translation-a.translation).length for a,b in zip(camera_path,camera_path[1:])];angles=[qangle(a,b) for a,b in zip(camera_path,camera_path[1:])];accels=[(c.translation-2*b.translation+a.translation).length for a,b,c in zip(camera_path,camera_path[1:],camera_path[2:])]
 metric.update(max_camera_step_m=max(steps),max_camera_rotation_deg=max(angles),max_camera_accel_m_per_frame2=max(accels))
 if max(angles)>8:errors.append(['camera rotation jump',max(angles)])
 result={'variant':variant,'pass_all':not errors,'errors':errors,'samples':len(times),'original_geometry_equal':True,'approved_geometry_additions':['MP_CONTINUOUS_ROAD'],'approved_pose_scope':'wheel US-space Z only; all other actors and wheel XY/rotation checked against source','fps':24,'output_end':s.frame_end,'metrics':metric,'camera_joins':joins,'events':event_rows,'source_sha256':sha(R/'inputs/source.blend'),'blend_sha256':sha(path),'script_sha256':sha(__file__),'config_sha256':sha(R/'config.json'),'scope':'All actors matched at source quarter-frames, all output integer frames, S5 1/16-frame contact samples and event +/-2 source frames at 1/16. Direct truck wheel ray support, hitch, door/body SAT, container support, ship water, hand support. Camera box bounds exclude globe surfaces.'}
 (R/'review'/f'validation-{variant}.json').write_text(json.dumps(result,indent=2),encoding='utf8');print('RESULT',variant,json.dumps({'errors':errors,'metrics':metric}),flush=True)
 assert not errors,result

