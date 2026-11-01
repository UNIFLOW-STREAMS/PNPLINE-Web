"""Compare the saved files and test clearance against the evaluated replacement meshes."""
import bpy, bmesh, hashlib, json, sys
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = root.parent/'us-warehouse-curvature-v001/pnpline-us-warehouse-curvature-v001.blend'
candidate = root/'pnpline-container-ship-v001.blend'
sys.path.insert(0,str(root.parents[1]/'blockout/us-title-curve-v001/scripts'))
from audit_preservation import action_signature, minimize_scene, motion_names, optics, visible

def digest(path):
    with path.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()

def mesh(o):
    ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get()); me=ev.to_mesh()
    pts=[v.co.copy() for v in me.vertices]; faces=[p.vertices[:] for p in me.polygons]
    ev.to_mesh_clear()
    return pts,faces

def gather(s):
    ship=s.objects['A02_SHIP']
    stat=[o for o in ship.children_recursive if o.name.startswith('VSL_')]
    pts=[];faces=[];owners=[]
    for o in stat:
        vertices,polys=mesh(o);offset=len(pts);m=ship.matrix_world.inverted()@o.matrix_world
        pts.extend(m@p for p in vertices);faces.extend(tuple(j+offset for j in p) for p in polys)
        owners.extend([o.name]*len(polys))
    return BVHTree.FromPolygons(pts,faces),owners

def around(s, tree, owners, objects):
    inverse=s.objects['A02_SHIP'].matrix_world.inverted()
    bbox=[(-8.20,9.20),(-2.85,2.65),(-1.4,7.05)]
    contacts=set()
    for o in objects:
        m=inverse@o.matrix_world
        corners=[m@Vector(p) for p in o.bound_box]
        if any(max(p[i] for p in corners)<lo or min(p[i] for p in corners)>hi for i,(lo,hi) in enumerate(bbox)):continue
        pts,fs=mesh(o)
        if not fs:continue
        other=BVHTree.FromPolygons([m@p for p in pts],fs)
        contacts.update((o.name,owners[k]) for k,j in tree.overlap(other))
    return sorted(contacts)

def motion(path):
    bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.frame_set(0)
    names=sorted(set(motion_names(s))|{'P02_SPREADER','P02_TROLLEY','P02_SPREADER_FRAME','A01_FLOOR','A01_ROOF'})
    actions={a.name:action_signature(a) for a in bpy.data.actions}
    contract=[s.camera.name,s.frame_start,s.frame_end,s.render.fps,s.render.fps_base,s.render.frame_map_old,s.render.frame_map_new,
              [(m.name,m.frame,m.camera.name if m.camera else None) for m in s.timeline_markers]]
    minimize_scene(s,names)
    objects=[s.objects[n] for n in names]
    result=np.empty((990,len(names),4,4),dtype='float32');camera=[]
    for f in range(990):
        s.frame_set(f)
        result[f]=[np.asarray(o.matrix_world) for o in objects]
        camera.append(optics(s.camera))
    return names,actions,contract,result,camera

original=motion(source);updated=motion(candidate)
assert original[0]==updated[0]
error=np.max(np.abs(original[3]-updated[3]),axis=(0,2,3))
report=dict(source_sha256=digest(source),result_sha256=digest(candidate),evaluated_frames=990,
            actors_world_matrix_max_error=dict(zip(original[0],map(float,error))),
            actions=len(original[1]),actions_equal=original[1]==updated[1],optics_equal=original[4]==updated[4],
            timeline_equal=original[2]==updated[2],actor_count=len(error))
print('MOTION',len(error),float(max(error)),flush=True)
bpy.ops.wm.open_mainfile(filepath=str(candidate));s=bpy.context.scene;s.frame_set(0)
col=next(c for c in bpy.data.collections if c.name.startswith('PNPLINE • container vessel'))
logo=[o for o in col.objects if o.name.startswith('VSL_Raised logo')]
nonmanifold=0
for o in logo:
    bm=bmesh.new();bm.from_mesh(o.data);nonmanifold+=sum(not e.is_manifold for e in bm.edges);bm.free()
report.update(logo_glyphs=len(logo),nonmanifold_logo_edges=nonmanifold,
              missing_external_images=[i.name for i in bpy.data.images if i.source=='FILE' and i.filepath and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).is_file()])
tree,owners=gather(s)
report['berth_intersections']={}
for frame in (60,360):
    s.frame_set(frame)
    quay=[o for o in s.objects if visible(o) and o.type=='MESH' and ('QUAY' in o.name or 'FENDER' in o.name or 'BOLLARD' in o.name or o.name.startswith('PORT_EDGE'))]
    report['berth_intersections'][frame]=around(s,tree,owners,quay)
s.frame_set(0)
tools=[o for rootname in ('P01_SPREADER','P02_SPREADER') for o in s.objects[rootname].children_recursive if visible(o) and o.type=='MESH']
tool_names=[o.name for o in tools];report['spreader_meshes']=tool_names
minimize_scene(s,['A02_SHIP','A01_CONTAINER']+tool_names)
ship=s.objects['A02_SHIP'];cargo=s.objects['A01_CONTAINER']
box=[Vector((x,y,z)) for x in (-1.598,1.598) for y in (-.783,.783) for z in (-.747,.747)]
fs=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
contacts={};errors=[];landed=[]
times=sorted(set(range(466))|{f+.5 for f in range(75)}|{f+.5 for f in range(350,430)})
for t in times:
    s.frame_set(int(t),subframe=t-int(t))
    m=ship.matrix_world.inverted()@cargo.matrix_world
    if abs(m.translation.x)<12 and abs(m.translation.y)<5 and m.translation.z<9:
        other=BVHTree.FromPolygons([m@p for p in box],fs)
        for k in {i for i,j in tree.overlap(other)}:contacts.setdefault('cargo / '+owners[k],set()).add(t)
    for name,hit in around(s,tree,owners,tools):contacts.setdefault(name+' / '+hit,set()).add(t)
    if 60<=t<=360 and int(t)==t:
        for dx,dy in [(0,0),(-1.49,-.66),(-1.49,.66),(1.49,-.66),(1.49,.66)]:
            bottom=m@Vector((dx,dy,-.75));p,_,ind,_=tree.ray_cast(bottom+Vector((0,0,.08)),Vector((0,0,-1)),.17)
            if p is None:errors.append([t,dx,dy,'no support'])
            else:
                landed.append(abs(bottom.z-p.z))
                if abs(bottom.z-p.z)>.00015:errors.append([t,dx,dy,bottom.z-p.z])
report.update(handoff_samples=len(times),cargo_spreader_intersections={k:sorted(v) for k,v in contacts.items()},
              support_mismatches=errors,support_frames=[60,360],support_probes=len(landed),max_landing_gap=max(landed))
report['pass']=bool(max(error)==0 and all(report[k] for k in ('actions_equal','optics_equal','timeline_equal')) and not any(report['berth_intersections'].values()) and not contacts and not errors and not nonmanifold and len(logo)==14 and not report['missing_external_images'])
(root/'review/verification.json').write_text(json.dumps(report,indent=2))
print('VERIFY',report['pass'],len(contacts),errors[:5],report['berth_intersections'],flush=True)
assert report['pass']
