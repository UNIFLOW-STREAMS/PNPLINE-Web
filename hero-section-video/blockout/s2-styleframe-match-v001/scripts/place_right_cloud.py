"""Place the existing right cloud behind A; change only its root location."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(156)
out=Path(sys.argv[sys.argv.index('--')+1]);assert not out.exists()
root=s.objects['SF_CLOUD_RIGHT'];before=root.location.copy();cam=s.camera
def bounds(objects):
 ps=[world_to_camera_view(s,cam,o.matrix_world@Vector(v)) for o in objects if o.type in ['MESH','CURVE'] for v in o.bound_box]
 return [min(p.x for p in ps),min(p.y for p in ps),max(p.x for p in ps),max(p.y for p in ps)]
ab=bounds([s.objects['SF_CHINA_GOLD_A']]);target=Vector((ab[2]-.020,ab[1]+.30*(ab[3]-ab[1])))
# Moving away along the viewing ray creates genuine letter/cloud depth order.
world=root.matrix_world.translation.copy();origin=cam.matrix_world.translation;world+=(world-origin).normalized()*6
root.location=root.parent.matrix_world.inverted()@world;bpy.context.view_layer.update()
# Screen-centre alignment changes only a static world-space position at f156.
right=cam.matrix_world.to_3x3()@Vector((1,0,0));up=cam.matrix_world.to_3x3()@Vector((0,1,0))
for _ in range(5):
 cb=bounds(root.children_recursive);center=Vector(((cb[0]+cb[2])/2,(cb[1]+cb[3])/2));p=root.matrix_world.translation.copy()
 q=world_to_camera_view(s,cam,p);qr=world_to_camera_view(s,cam,p+right);qu=world_to_camera_view(s,cam,p+up)
 p+=right*((target.x-center.x)/(qr.x-q.x))+up*((target.y-center.y)/(qu.y-q.y))
 root.location=root.parent.matrix_world.inverted()@p;bpy.context.view_layer.update()
version=out.stem.rsplit('-',1)[-1]
(R/f'review/right-cloud-placement-{version}.json').write_text(json.dumps({'source':bpy.data.filepath,'before':list(before),'after':list(root.location),'target_center':list(target),'change':'SF_CLOUD_RIGHT.location only'},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(out))
