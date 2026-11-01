import bpy,sys,json
from pathlib import Path
from collections import Counter
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R.parents[1]/'blockout/us-title-curve-v001/scripts'))
from audit_preservation import motion_names,minimize_scene,optics,action_signature
import numpy as np
def motion(s):
    s.frame_set(0)
    names=sorted(motion_names(s));actions={a.name:action_signature(a) for a in bpy.data.actions}
    timings=[s.frame_start,s.frame_end,s.render.fps,[(m.name,m.frame) for m in s.timeline_markers]]
    minimize_scene(s,names);obs=[s.objects[n] for n in names];result=[];lenses=[]
    for f in range(990):
        s.frame_set(f);result.append([np.asarray(o.matrix_world) for o in obs]);lenses.append(optics(s.camera))
    return names,actions,timings,np.asarray(result),lenses
s=bpy.context.scene
build=json.loads((R/'review/build.json').read_text())
trees=[o for o in s.objects if o.name.startswith('WC | ')]
assert len(trees)==build['total_trees'] and len(set(o.data for o in trees))==2
assert all(o.matrix_world.determinant()>0 for o in trees)
print('tree heights',[round(min(o.scale.z for o in trees),4),round(max(o.scale.z for o in trees),4)],flush=True)
assert all(s.objects[n].material_slots[-1].material.name=='PNPLINE | white enamel' for n in build['logo_objects'])
assert list(bpy.data.materials['PNPLINE | white enamel'].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value)==[1,1,1,1]
assert all(slot.material.name=='A01 | pearl grey' for o in s.objects['A01_CONTAINER'].children_recursive if o.name in ('A01_SIDE_L','A01_SIDE_R','A01_FLOOR','A01_ROOF','A01_FRONT','A01_DOOR_LEFT_LEAF','A01_DOOR_RIGHT_LEAF','FLT_Intermodal pressed freight body') for slot in o.material_slots)
assert len([o for o in s.objects if o.name.startswith('DSP_TREEBED_') and not o.hide_render])==67
b=motion(s)
bpy.ops.wm.open_mainfile(filepath=str(R.parent/'hero-material-v001/pnpline-hero-material-v001.blend'))
a=motion(bpy.context.scene)
assert a[:3]==b[:3] and a[4]==b[4];delta=float(np.max(np.abs(a[3]-b[3])));assert delta==0
(R/'review/verification.json').write_text(json.dumps(dict(trees=len(trees),tree_types=build['types'],planters=67,logo_objects=len(build['logo_objects']),frames=990,matched_actions=len(a[1]),tracked_objects=len(a[0]),max_world_matrix_delta=delta,pass_all=True),indent=2))
