"""The reference cloud peeks from behind the lower-right edge of A."""
import bpy,sys,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(156)
def bounds(objects):
 points=[world_to_camera_view(s,s.camera,o.matrix_world@Vector(v)) for o in objects if o.type in ['MESH','CURVE'] for v in o.bound_box]
 return [min(p.x for p in points),min(p.y for p in points),max(p.x for p in points),max(p.y for p in points)]
a=s.objects['SF_CHINA_GOLD_A'];cloud=s.objects['SF_CLOUD_RIGHT'];ab=bounds([a]);cb=bounds(cloud.children_recursive)
center=(cb[1]+cb[3])/2;relative_height=(center-ab[1])/(ab[3]-ab[1])
# Cast from sampled cloud body surfaces to determine actual A occlusion.
origin=s.camera.matrix_world.translation;inv=a.matrix_world.inverted();hidden=total=0
for o in cloud.children_recursive:
 if o.type!='MESH':continue
 for v in list(o.data.vertices)[::8]:
  p=o.matrix_world@v.co;d=(p-origin).normalized();hit,q,_,_=a.ray_cast(inv@origin,(inv.to_3x3()@d).normalized())
  total+=1
  if hit and (a.matrix_world@q-origin).length<(p-origin).length-.01:hidden+=1
ratio=hidden/max(total,1)
result={'blend':bpy.data.filepath,'a_bounds':ab,'cloud_bounds':cb,'cloud_location':list(cloud.location),'a_location':list(a.parent.location),'relative_height':relative_height,'a_occlusion_fraction':ratio,'tests':{'lower_right_position':.18<relative_height<.42,'partly_behind_a':.20<ratio<.70,'extends_right':cb[2]>ab[2]}}
suffix=sys.argv[sys.argv.index('--')+1] if '--'in sys.argv else 'result'
(R/f'review/right-cloud-{suffix}.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
assert all(result['tests'].values()),'Cloud must occupy the lower-right flank and be partially occluded by A'
