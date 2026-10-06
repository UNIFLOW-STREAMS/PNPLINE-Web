"""Translate camera upward without changing any camera rotation or lens keys."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[1];S=bpy.context.scene;cam=S.camera;target=bpy.data.objects['CAM_LOOK_TARGET']
assert Path(bpy.data.filepath).resolve()==(ROOT/'inputs/base-v002.blend').resolve()
assert cam.parent is None and target.parent is None
base=json.loads((ROOT/'inputs/base-camera.json').read_text())
S.frame_set(0)
# The fixed China port is on a spherical world. Its vertical is its surface
# normal in world coordinates, so altitude rises while screen alignment stays.
up=(bpy.data.objects['CN_FRAME'].matrix_world.to_3x3()@Vector((0,0,1))).normalized()
origin=Matrix(base['frames'][0]['matrix']).translation
obj=bpy.data.objects['A01_CONTAINER']
def lower_edge(h):
 cam.location=origin+up*h;bpy.context.view_layer.update()
 return min(world_to_camera_view(S,cam,obj.matrix_world@Vector((x,y,z))).y for x in [-1.6,1.6] for y in [-.8,.8] for z in [-.75,.75])
lo,hi=0.0,2.0
for _ in range(32):
 h=(lo+hi)/2
 if lower_edge(h)>.09:lo=h
 else:hi=h
height=(lo+hi)/2
for f in range(96):
 S.frame_set(f);t=f/96;weight=1-(10*t**3-15*t**4+6*t**5)
 shift=up*(height*weight)
 cam.location=Matrix(base['frames'][f]['matrix']).translation+shift
 target.location=Vector(base['frames'][f]['target'])+shift
 cam.keyframe_insert('location',frame=f);target.keyframe_insert('location',frame=f)
for o in [cam,target]:
 for layer in o.animation_data.action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for fc in bag.fcurves:
     if fc.data_path=='location':
      for kp in fc.keyframe_points:
       if kp.co.x<96:kp.interpolation='LINEAR'
guide=bpy.data.objects.get('CAMERA_PATH')
if guide and guide.type=='CURVE':
 for p,f in zip(guide.data.splines[0].points,range(1,1393,6)):
  S.frame_set(f);p.co=(*cam.matrix_world.translation,1)
S['master_version']='v003';S['camera_revision']='S1 starting camera raised; rotations and lens unchanged; translation offset fades to zero at frame 96'
S['generator']='scripts/raise_camera.py applied to inputs/base-v002.blend'
S.name='PNPLINE_MASTER_v003';S.render.filepath=str(ROOT/'preview/frames/frame-');S.frame_set(0)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'master-v003.blend'))
result={'height_offset_at_0':height,'world_translation_at_0':list(up*height),'direction':'fixed China port surface vertical expressed in world coordinates','changed_camera_translation_frames':[0,95],'unchanged_rotation_frames':[0,1392],'unchanged_lens_frames':[0,1392],'unchanged_camera_from_frame':96,'frame0_container_bottom_ndc':lower_edge(height),'reference':'inputs/framing-reference.png'}
(ROOT/'review/revision.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
