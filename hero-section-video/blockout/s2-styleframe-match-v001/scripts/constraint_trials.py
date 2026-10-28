"""Unsaved visual-only diagnostic trials. Protected transforms/actions untouched.
Not production art; no trial is promoted to master. Each render reloads base.
"""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
def render(name):
 s=bpy.context.scene;s.frame_set(156)
 s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
 s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True
 s.render.image_settings.file_format='PNG';s.render.filepath=str(R/'review'/name);bpy.ops.render.render(write_still=True)
def load():bpy.ops.wm.open_mainfile(filepath=str(R/'inputs/base.blend'));bpy.context.scene.frame_set(156)
load()
# Literal exterior reversal around its own protected root, containers unchanged.
# Shows why an exterior-only change cannot solve direction or cargo clearance.
for n in ['SHIP_HULL','SHIP_DECK','SHIP_BRIDGE','SHIP_BRIDGE_GLASS']:
 o=bpy.data.objects[n];o.location.x=-o.location.x;o.location.y=-o.location.y;o.rotation_euler.z+=math.pi
render('trial-exterior-reversed.png')
load()
# Bring static upper crane beams down to the target apex screen height.
# All animated trolley/cables/spreader remain at their protected actual poses.
s=bpy.context.scene;cam=s.camera;cn=s.objects['CN_FRAME'].matrix_world
from bpy_extras.object_utils import world_to_camera_view
def py(z):return 1-world_to_camera_view(s,cam,cn@Vector((.75,4,z))).y
lo,hi=0,14
for _ in range(50):
 mid=(lo+hi)/2
 if py(mid)>550/1156:lo=mid
 else:hi=mid
z=(lo+hi)/2;factor=z/11.9
for o in s.objects:
 if o.name.startswith(('P01_LEG_','P01_BOOM_')):
  o.location.z*=factor;o.scale.z*=factor
render('trial-static-crane-lowered.png')
(R/'review/trial-settings.json').write_text(json.dumps({'status':'diagnostic only, unsaved; NOT adopted; not a style match','ship':'visual hull/deck/bridge rotated 180 around protected root; cargo/root/action unchanged','crane':{'original_beam_height':11.9,'trial_beam_height':z,'factor':factor,'trolley_cable_animation':'unchanged'},'camera':'CAM_MASTER original f156'},indent=2))
