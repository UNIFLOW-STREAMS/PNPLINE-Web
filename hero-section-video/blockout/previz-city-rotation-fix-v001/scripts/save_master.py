import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;source=Path(bpy.data.filepath);out=R/'master-previz-city-rotation-fix-v001.blend';assert not out.exists()
s['previz_status']='Adopted city rotation, contact corrected; verification accompanies delivery'
s['route_b_status']='City rotation selected by user; original B route not adopted'
s['city_rotation_contact_fix']='City shore separation, adapted/parked crane, US arrival slope, sea-sealed coast'
s.frame_set(156);s.use_preview_range=False
for screen in bpy.data.screens:
 for ar in screen.areas:
  if ar.type=='VIEW_3D':ar.spaces.active.region_3d.view_perspective='CAMERA';ar.spaces.active.shading.type='SOLID';ar.spaces.active.shading.color_type='MATERIAL'
bpy.ops.wm.save_as_mainfile(filepath=str(out))
(R/'delivery.json').write_text(json.dumps({'file':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'baseline':str(R/'inputs/base.blend'),'baseline_sha256':hashlib.sha256((R/'inputs/base.blend').read_bytes()).hexdigest(),'candidate':str(source),'candidate_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'status':'Saved; final verification in progress','timeline':[s.frame_start,s.frame_end,s.render.fps,s.render.fps_base],'adopted_option':'city rotation'},indent=2))
