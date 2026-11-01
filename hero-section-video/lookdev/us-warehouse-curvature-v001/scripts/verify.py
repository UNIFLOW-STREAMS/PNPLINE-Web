import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];B=R.parents[1]/'blockout'
sys.path[:0]=[str(R/'scripts'),str(B/'us-title-curve-v001/scripts'),str(B/'curvature-rework-v001/scripts')]
from surface_site import *
from audit_preservation import minimize_scene,action_signature
s=bpy.context.scene;w=s.objects;u=w['US_FRAME'];ui=u.matrix_world.inverted()
build=json.loads((R/'review/build.json').read_text())
source=R/'before.blend';candidate=Path(bpy.data.filepath)
result={'file':str(candidate),'removed_absent':all(n not in w for n in build['removed'])}
sig={a.name:action_signature(a) for a in bpy.data.actions}
contract=lambda s:[s.camera.name,s.frame_start,s.frame_end,s.render.fps,s.render.fps_base,s.render.frame_map_old,s.render.frame_map_new,[(m.name,m.frame) for m in s.timeline_markers]]
after_contract=contract(s)
missing=[]
for im in bpy.data.images:
    if im.source=='FILE' and im.filepath and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).exists():missing.append(im.filepath)
result['missing_images']=missing
back=[]
for name in build['rear']:
    o=w[name];m=ui@o.matrix_world;up=(m.to_3x3()@Vector((0,0,1))).normalized()
    n=(m.translation-Vector(C)).normalized()
    back.append([name,round(np.linalg.norm(np.array(m.translation)-C)-140,5),np.degrees(up.angle(n))])
result['rear_radial_alignment_degrees_max']=float(max(b[2] for b in back));result['rear_ground_anchor_heights']=[min(b[1] for b in back),max(b[1] for b in back)]
def tree(ns):
    pts=[];faces=[]
    for name in ns:
        if name not in w:continue
        o=w[name];mat=ui@o.matrix_world;start=len(pts);pts.extend(mat@v.co for v in o.data.vertices)
        faces.extend(tuple(start+i for i in f.vertices) for f in o.data.polygons)
    return BVHTree.FromPolygons(pts,faces)
ground=tree(['US_LAND_TERRACE','DSP_CONTINUOUS_GROUND','CE_NY_CURVED_LAND','CE_CHICAGO_CURVED_LAND']+[o.name for o in s.objects if o.get('ce_role')=='curved_terrain' and 'REAR' in o.name])
def hit(b,x,y):
    n=Vector(sphere(np.array([x,y,0]))-C).normalized()
    v,_,_,_=b.ray_cast(Vector(C)+143*n,-n,5)
    return None if v is None else (v-Vector(C)).length-140
result['warehouse_land_samples']=[[x,y,hit(ground,x,y)] for x in (25,29,36,44,52,60,68,75,81) for y in (24,29,32,38)]
result['rear_land_samples']=[[o,*w[o]['ce_anchor'][:2],hit(ground,*w[o]['ce_anchor'][:2])] for o in build['rear']]
floor=tree(['WAREHOUSE_FLOOR'])
yard=tree(['E10_OUTBOUND_YARD']);maneuver=tree(['E09_MANEUVER_YARD'])
result['finish_altitudes']={n:[[x,y,hit(obj,x,y)] for x in xs for y in ys] for n,obj,xs,ys in [('warehouse',floor,(37,44,52,60,67),(27,32,38)),('dispatch_apron',yard,(68.2,72,77,81.8),(24,30,36)),('maneuver_yard',maneuver,(18,26,30,35,38),(27,31))]}
def height_error(samples,wanted):
    return max(abs(z-wanted) for _,_,z in samples if z is not None)
result['apron_max_radial_error']=height_error(result['finish_altitudes']['dispatch_apron'],.76)
result['warehouse_floor_max_radial_error']=height_error(result['finish_altitudes']['warehouse'],1.86)
result['maneuver_yard_max_radial_error']=height_error(result['finish_altitudes']['maneuver_yard'],.76)
data=np.load(R/'review/motion-baseline.npz')
names=[n for n in data.files if n not in {'camera','target','optics'}]
s.frame_set(0);minimize_scene(s,names+['CAM_MASTER','CAM_LOOK_TARGET'])
delta={n:0. for n in names};camera=target=optics=0.
for f in range(990):
    s.frame_set(f)
    for n in names:delta[n]=max(delta[n],np.max(np.abs(np.array(w[n].matrix_world)-data[n][f])))
    camera=max(camera,np.max(abs(np.array(w['CAM_MASTER'].matrix_world)-data['camera'][f])))
    target=max(target,np.max(abs(np.array(w['CAM_LOOK_TARGET'].matrix_world)-data['target'][f])))
    cd=w['CAM_MASTER'].data
    optics=max(optics,np.max(abs(np.array([cd.lens,cd.dof.focus_distance,cd.dof.aperture_fstop])-data['optics'][f])))
result['original_camera_target_optics_max_abs_error']=[float(camera),float(target),float(optics)]
result['surface_actor_fit_max_abs_error']={k:float(v) for k,v in delta.items()}
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
result['changed_original_actions']=[a.name for a in bpy.data.actions if sig.get(a.name)!=action_signature(a)]
result['timing_and_markers_exact']=contract(s)==after_contract
result['native_frames_compared']=990
result['pass']=bool(result['removed_absent'] and max(camera,target,optics)<1.e-6 and max(delta.values())<.001 and result['timing_and_markers_exact'] and not result['changed_original_actions'] and max(result['apron_max_radial_error'],result['maneuver_yard_max_radial_error'],result['warehouse_floor_max_radial_error'])<.02 and result['rear_radial_alignment_degrees_max']<.08)
(R/'review/verification.json').write_text(json.dumps(result,indent=2))
print('verification',result['pass'],'camera',camera,target,optics,'motion',max(delta.values()),'floor',result['warehouse_floor_max_radial_error'],'apron',result['apron_max_radial_error'],'missing ground',[(x,y) for x,y,h in result['warehouse_land_samples'] if h is None],flush=True)
assert result['pass'],'See verification.json'
