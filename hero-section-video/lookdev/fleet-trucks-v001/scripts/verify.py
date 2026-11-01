import bpy,bmesh,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import numpy as np
R=Path(__file__).resolve().parents[1]
B=R.parents[1]/'blockout'
src=R.parent/'container-ship-v001/pnpline-container-ship-v001.blend'
dst=R/'pnpline-fleet-trucks-v001.blend'
sys.path.insert(0,str(B/'us-title-curve-v001/scripts'))
from audit_preservation import action_signature,minimize_scene,motion_names,optics,visible
build=json.loads((R/'review/build.json').read_text())
wheel_names=build['wheel_objects']
def sha(file):
    with file.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def capture(path):
    bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.frame_set(0)
    names=sorted(set(motion_names(s))|set(wheel_names)|{'W08_LAST_LOAD','A01_DOOR_L','A01_DOOR_R','A01_FLOOR','A01_ROOF','P02_SPREADER'})
    actions={a.name:action_signature(a) for a in bpy.data.actions}
    timing=[s.camera.name,s.frame_start,s.frame_end,s.render.fps,s.render.fps_base,s.render.frame_map_old,s.render.frame_map_new,[(m.frame,m.name) for m in s.timeline_markers]]
    vals=np.empty((990,len(names),4,4),np.float32);lenses=[];bottom=np.empty((990,len(wheel_names)))
    # Compare the supporting contour against the old rotating tyres.
    radii=[]
    for n in wheel_names:
        xy=np.array([v.co[:] for v in s.objects[n].data.vertices])
        r=np.sqrt(np.sum(xy[:,:2]**2,axis=1));radii.append(np.unique(xy[r>max(r)-1e-5],axis=0))
    minimize_scene(s,names)
    objects=[s.objects[n] for n in names];wheels=[s.objects[n] for n in wheel_names]
    for f in range(990):
        s.frame_set(f);vals[f]=[np.asarray(o.matrix_world) for o in objects];lenses.append(optics(s.camera))
        for j,(o,pts) in enumerate(zip(wheels,radii)):
            m=np.asarray(o.parent.matrix_world.inverted()@o.matrix_world)
            bottom[f,j]=np.min(pts@m[2,:3])+m[2,3]
    return names,actions,timing,vals,lenses,bottom
source=capture(src);result=capture(dst)
assert source[0]==result[0]
report=dict(source_sha256=sha(src),result_sha256=sha(dst),native_frames=990, tracked_objects=len(source[0]),actions=len(source[1]),
            action_curves_equal=source[1]==result[1],timing_equal=source[2]==result[2],optics_equal=source[4]==result[4],
            max_world_matrix_delta=float(np.max(abs(source[3]-result[3]))),max_tire_contact_delta=float(np.max(abs(source[5]-result[5]))))
print('Motion',report,flush=True)
def gather(seq,anchor):
    pts=[];fs=[]
    inverse=anchor.matrix_world.inverted();dg=bpy.context.evaluated_depsgraph_get()
    for obj in seq:
        ev=obj.evaluated_get(dg);m=inverse@ev.matrix_world;me=ev.to_mesh();base=len(pts)
        pts.extend(m@v.co for v in me.vertices);fs.extend(tuple(i+base for i in f.vertices) for f in me.polygons);ev.to_mesh_clear()
    return BVHTree.FromPolygons(pts,fs)
faces=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
def bounds(bounds,m):
    pts=[m@Vector((x,y,z)) for x in bounds[0] for y in bounds[1] for z in bounds[2]]
    return BVHTree.FromPolygons(pts,faces)
def pose_key(m):return tuple(round(v,3) for row in m for v in row)
bpy.ops.wm.open_mainfile(filepath=str(dst));s=bpy.context.scene;s.frame_set(0);w=s.objects
report['cranes_absent']=all(w.get(n) is None for n in build['removed_cranes'])
report['working_cranes_present']=all(w.get(n) and not w[n].hide_render for n in ('P02_SPREADER_FRAME','P02_BOOM_-2','CR_TWISTLOCK','PT_CRANE_WEST_cyan','PT_CRANE_EAST_cyan'))
report['missing_images']=[i.name for i in bpy.data.images if i.source=='FILE' and i.filepath and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).is_file()]
logos=[o for o in w if o.name.startswith('FLT_') and 'glyph_index' in o]
groups={};nonmanifold=0
for o in logos:
    key=(o.parent.name,o['side']);groups.setdefault(key,[]).append((o['glyph_index'],np.mean([v.co.x for v in o.data.vertices])))
    bm=bmesh.new();bm.from_mesh(o.data);nonmanifold+=sum(not e.is_manifold for e in bm.edges);bm.free()
report.update(relief_glyphs=len(logos),nonmanifold_logo_edges=nonmanifold,logo_sides={str(k):len(v) for k,v in groups.items()},
              outward_readable=len(groups)==6 and all(len(v)==7 and all((b[1]-a[1])*k[1]<0 for a,b in zip(sorted(v),sorted(v)[1:])) for k,v in groups.items()))
ship=w['A02_SHIP'];box=w['A01_CONTAINER'];trailer=w['A03_TRAILER'];tractor=w['A03_TRACTOR'];van=w['A04_PRIMARY']
ship_tree=gather([o for o in ship.children_recursive if o.name.startswith('VSL_') and visible(o)],ship)
cab_tree=gather([o for o in tractor.children if o.name.startswith(('FLT_Inbound cab','FLT_Inbound glazing','FLT_Inbound lights'))],tractor)
bed=gather([o for o in trailer.children if o.name.startswith('FLT_')],trailer)
dispatch=gather([o for o in van.children if o.name.startswith('FLT_') and o.type=='MESH'],van)
load=w['W08_LAST_LOAD'];cargo_bounds=[(-1.711,1.616),(-.794,.794),(-.747,.75)]
last_box=next(o for o in load.children if o.type=='MESH')
minimize_scene(s,[k.name for k in (ship,box,trailer,tractor,van,load,last_box)])
ship_hits=[];cab_hits=[];dispatch_hits=[];keys=[set(),set()];max_gap=0;bed_checks=0
frames=sorted(set(range(990))|{i+.5 for i in range(75)}|{i+.5 for i in range(350,465)}|{i+j/4 for i in range(527,556) for j in (1,2,3)})
for f in frames:
    s.frame_set(int(f),subframe=f%1)
    for i,(parent,tree,fail) in enumerate(((ship,ship_tree,ship_hits),(tractor,cab_tree,cab_hits))):
        m=parent.matrix_world.inverted()@box.matrix_world
        if m.translation.length>14:continue
        key=pose_key(m)
        if key in keys[i]:continue
        keys[i].add(key)
        if tree.overlap(bounds(cargo_bounds,m)):fail.append(f)
    if f>=465 and f==int(f):
        m=trailer.matrix_world.inverted()@box.matrix_world
        for dx,dy in [(0,0),(-1.46,-.63),(1.46,-.63),(-1.46,.63),(1.46,.63)]:
            bottom=m@Vector((dx,dy,-.75))
            p,*_=bed.ray_cast(bottom+Vector((0,0,.08)),Vector((0,0,-1)),.18)
            if p is None:max_gap=99
            else:max_gap=max(max_gap,abs(bottom.z-p.z))
            bed_checks+=1
    if 800<=f<=895:
        m=van.matrix_world.inverted()@last_box.matrix_world
        corners=list(zip(*last_box.bound_box))
        if dispatch.overlap(bounds([(min(a),max(a)) for a in corners],m)):dispatch_hits.append(f)
report.update(ship_cargo_envelope_intersections=ship_hits,cab_cargo_envelope_intersections=cab_hits,
              dispatch_new_fittings_parcel_intersections=dispatch_hits,sampled_times=len(frames),trailer_support_samples=bed_checks,trailer_max_gap=max_gap)
report['pass']=bool(all(report[k] for k in ('action_curves_equal','timing_equal','optics_equal','cranes_absent','working_cranes_present','outward_readable')) and
    report['max_world_matrix_delta']==0 and report['max_tire_contact_delta']<.016 and max_gap<.0005 and not (ship_hits or cab_hits or dispatch_hits or nonmanifold or report['missing_images']))
(R/'review/verification.json').write_text(json.dumps(report,indent=2))
print('RESULT',report,flush=True);assert report['pass']
