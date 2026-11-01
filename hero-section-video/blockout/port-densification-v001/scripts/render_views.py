import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;source=Path(bpy.data.filepath);sha=hashlib.sha256(source.read_bytes()).hexdigest()
folder=R/'review/views';folder.mkdir(exist_ok=True,parents=True)
for f in [300,315,349,390,420,450,480,505,530]:
 s.frame_set(f);s.render.filepath=str(folder/f'timeline-{f:04}.png');bpy.ops.render.render(write_still=True)
s.frame_set(349);U=s.objects['US_FRAME'];data=bpy.data.cameras.new('PT_REVIEW_ONLY');cam=bpy.data.objects.new('PT_REVIEW_ONLY',data);s.collection.objects.link(cam);s.camera=cam
s.render.resolution_x=1600;s.render.resolution_y=900;s.render.resolution_percentage=100
for name,eye,target,scale in [('port-after',(-28,-40,33),(0,9,4),65),('port-top-after',(0,12,65),(0,12,0),62),('port-detail',(-15,-10,16),(-7,10,3),30),('quay-side',(0,-45,19),(0,9,3),55)]:
 eye=Vector(eye);target=Vector(target);q=(target-eye).to_track_quat('-Z','Y');cam.matrix_world=U.matrix_world@Matrix.Translation(eye)@q.to_matrix().to_4x4();data.type='ORTHO';data.ortho_scale=scale
 s.render.filepath=str(R/'preview'/f'{name}.png');bpy.ops.render.render(write_still=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
(R/'review/views.json').write_text(json.dumps({'sha256':sha,'timeline_frames':[300,315,349,390,420,450,480,505,530]}))
