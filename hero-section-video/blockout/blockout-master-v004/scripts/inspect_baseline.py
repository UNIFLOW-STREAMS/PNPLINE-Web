import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT=Path(__file__).resolve().parents[1]
s=bpy.context.scene
c=s.camera
t=bpy.data.objects.get('CAM_LOOK_TARGET')
ship=bpy.data.objects.get('A02_SHIP')
result={'filepath':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'scene':s.name,'metadata':dict(s.items()),'fps':s.render.fps/s.render.fps_base,'frames':[s.frame_start,s.frame_end],'markers':{m.name:m.frame for m in s.timeline_markers},'object_count':len(s.objects),'camera':c.name,'camera_constraints':[x.type for x in c.constraints],'camera_parent':c.parent.name if c.parent else None,'frames_sample':[]}
for f in [95,96,97,110,130,145,160,180,200,215,216,217]:
    s.frame_set(f)
    local=ship.matrix_world.inverted()@c.matrix_world.translation
    bounds=[]
    for obj in [ship,bpy.data.objects.get('A01_CONTAINER')]:
        meshes=[o for o in [obj,*obj.children_recursive] if o.type=='MESH']
        points=[world_to_camera_view(s,c,o.matrix_world@Vector(v)) for o in meshes for v in o.bound_box]
        bounds.append({'object':obj.name,'bounds':[min(p.x for p in points),min(p.y for p in points),max(p.x for p in points),max(p.y for p in points)]})
    result['frames_sample'].append({'frame':f,'position':list(c.matrix_world.translation),'rotation':list(c.matrix_world.to_quaternion()),'target':list(t.matrix_world.translation),'lens':c.data.lens,'ship_local_camera':list(local),'projected_bounds':bounds})
result['projection_note']='Projected mesh bounds include occluded vertices; not a visibility verdict.'
(ROOT/'review/baseline-inspection.json').write_text(json.dumps(result,indent=2,default=str),encoding='utf-8')
print('Saved baseline inspection', result['sha256'])
