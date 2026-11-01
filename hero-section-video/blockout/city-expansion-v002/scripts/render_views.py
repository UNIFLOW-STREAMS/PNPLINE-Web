import bpy,sys,json,hashlib,math
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'curvature-rework-v001/scripts'))
from mapping import surface,normal
s=bpy.context.scene;U=s.objects['US_FRAME'];source=Path(bpy.data.filepath);sha=hashlib.sha256(source.read_bytes()).hexdigest()
folder=R/'review/views';folder.mkdir(parents=True,exist_ok=True)
original=s.camera
for f in ([] if '--bookmarks-only' in sys.argv else [290,300,315,330,349,390,450,530,660,760,900,989]):
 s.frame_set(f);s.render.filepath=str(folder/f'timeline-{f:04}.png');bpy.ops.render.render(write_still=True)
data=bpy.data.cameras.new('CE_REVIEW_ONLY_CAMERA');cam=bpy.data.objects.new('CE_REVIEW_ONLY_CAMERA',data);s.collection.objects.link(cam);s.camera=cam
s.render.resolution_x=1600;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.frame_set(349)
bookmarks=[]
def capture(name,eye,target,scale=None,up=(0,0,1)):
 eye,target=Vector(eye),Vector(target);forward=(target-eye).normalized();right=forward.cross(Vector(up)).normalized();vertical=right.cross(forward)
 rotation=Matrix((right,vertical,-forward)).transposed().to_quaternion()
 cam.location=U.matrix_world@eye;cam.rotation_mode='QUATERNION';cam.rotation_quaternion=U.matrix_world.to_quaternion()@rotation
 data.type='ORTHO' if scale else 'PERSP';data.ortho_scale=scale or 100;data.lens=45;data.clip_end=1500
 s.render.filepath=str(folder/(name+'.png'));bpy.ops.render.render(write_still=True)
 bookmarks.append({'name':name,'matrix':list(map(list,cam.matrix_world)),'ortho':scale,'lens':45})
capture('overview-top',(25,5,215),(25,5,-8),245,(1,0,0))
capture('overview-oblique',(-45,-145,155),(24,6,-10),225,normal(24,6))
capture('rear-district',(22,140,100),(18,59,-4),125,normal(18,59))
for name,x,y in [('chrysler-detail',30,87),('pyramid-detail',43,-33.8),('willis-detail',18,-70),('bridge-detail',30,-6)]:
 T=Matrix.Translation(surface(x,y,.7))@Vector((0,0,1)).rotation_difference(normal(x,y)).to_matrix().to_4x4()
 capture(name,T@Vector((25,-35,27)),T@Vector((0,0,8)),54 if name!='bridge-detail' else 48,normal(x,y))
for name,x,y,h in [('wtc-detail',35,44,50),('needle-detail',-13,67,36),('rockefeller-detail',50,44,36)]:
 T=Matrix.Translation(surface(x,y,.7))@Vector((0,0,1)).rotation_difference(normal(x,y)).to_matrix().to_4x4()
 capture(name,T@Vector((35,40,h*.85)),T@Vector((0,0,h*.42)),h*1.65,normal(x,y))
assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
(R/'review/view-bookmarks.json').write_text(json.dumps({'sha256':sha,'resolution':[1600,1200],'bookmarks':bookmarks},indent=2))
