import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;j=json.loads((R/'source-map.json').read_text())
for row in j['objects']:
 o=s.objects[row['destination']];row['asset_id']=o.get('asset_id');row['instance_id']=o.get('instance_id');row['action']=o.animation_data.action.name if o.animation_data and o.animation_data.action else None;row['action_users']=o.animation_data.action.users if o.animation_data and o.animation_data.action else 0;row['parent_inverse']=list(map(list,o.matrix_parent_inverse))
(R/'source-map.json').write_text(json.dumps(j,indent=2,ensure_ascii=False))
s.frame_set(890);U=s.objects['US_FRAME'].matrix_world;data=bpy.data.cameras.new('INSPECTION_ONLY');cam=bpy.data.objects.new('INSPECTION_ONLY',data);s.collection.objects.link(cam);s.camera=cam;data.lens=56;cam.rotation_mode='QUATERNION'
s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
for label,f,p,t in [('dock-final',890,(38,26,3.9),(35.95,29,1.94)),('wheel-final',810,(27,24,2.8),(29,29,1.25)),('door-final',826,(33.4,25,3.7),(30.4,29,2.5))]:
 s.frame_set(f);p=Vector(p);t=Vector(t);cam.location=U@p;cam.rotation_quaternion=U.to_quaternion()@(t-p).to_track_quat('-Z','Y');s.render.filepath=str(R/'review'/f'{label}.png');bpy.ops.render.render(write_still=True)
